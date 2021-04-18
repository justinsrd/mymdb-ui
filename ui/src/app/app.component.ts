import {Component, OnInit} from '@angular/core';
import {Chart} from 'angular-highcharts';
import {MyServiceService} from './my-service.service';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss'],
    providers: [MyServiceService]
})
export class AppComponent implements OnInit {
    public searchMode = 'name';
    public searchText = '';
    public dataFetchInProgress = false;
    public recents: Array<{show_id: string, show_name: string, poster_url: string}>;
    private currentSeasons: number;
    private zoomYAxis = false;
    public errorMessage: string = null;
    public allShowData: any[];
    public showSeasonsLengthArr: any[];
    public chart: any = new Chart({
        chart: {
            type: 'scatter',
            animation: true,
            backgroundColor: '#142e45'
        },
        xAxis: {
            visible: false,
            tickWidth: 0
        },
        yAxis: {
            gridLineColor: '#424242',
            // min: 0,
            // max: 10
        },
        legend: {
            enabled: false
        },
        title: {
            text: '',
            style: {
                color: '#fff'
            }
        },
        credits: {
            enabled: false
        },
        series: [],
        tooltip: {
            useHTML: true,
            formatter: function() {
                const episode = this.point['episode'];
                return `
                    <div class="tooltip-container">
                        <p class="episode-title font-weight-bold">${episode.episode_title}</p>
                        <p class="episode-number">${episode.seriesNumber}</p>
                        <p class="episode-rating">
                            Rating: <span class="value font-weight-bold">${Number(episode.rating).toFixed(1)}</span>
                        </p>
                        <p class="episode-votes">Votes: </span class="value">${episode.votes}</span></p>
                    </div>
                `;
            }
        }
    });

    constructor(private myServiceService: MyServiceService) {

    }

    ngOnInit(): void {
        this.fetchRecentsOnly();
    }

    findColor(index: number) {
        const colors = ['#7ed1f0', '#f1ef85', '#cb78ed', '#7ff2ad', '#ef857c', '#80f2ea', '#7b8eed', '#b5f284', '#f079d3'];
        while (index > colors.length) {
            index -= colors.length;
        }
        return colors[index];
    }

    formatSeriesNumber(episode: any) {
        let str = 's';
        str += episode.season < 10 ? '0' + episode.season : episode.season;
        str += 'e';
        str += episode.episode < 10 ? '0' + episode.episode : episode.episode;
        return str;
    }

    switchy() {
        this.zoomYAxis = !this.zoomYAxis;
        if (this.zoomYAxis) {
            // const min = Math.max(Math.floor(this.chart.ref.yAxis[0].dataMin)-1, 0);
            // const max = Math.min(Math.ceil(this.chart.ref.yAxis[0].dataMax)+1, 10);
            // const min = Math.floor(this.chart.ref.yAxis[0].dataMin);
            // const max = Math.ceil(this.chart.ref.yAxis[0].dataMax);
            const min = this.chart.ref.yAxis[0].dataMin - .1;
            const max = this.chart.ref.yAxis[0].dataMax + .1;
            this.chart.ref.yAxis[0].setExtremes(min, max, true, true);
        } else {
            this.chart.ref.yAxis[0].setExtremes(0, 10);
        }
    }

    changeSeason(e) {
        const filter = e.target.value;
        if (filter === 'all') {
            this.renderChart(this.allShowData);
        } else {
            this.renderChart(this.allShowData.filter(episode => episode.season === Number(filter)));
        }
    }

    fetchData() {
        if (this.searchMode === 'name') {
            this.fetchByName(this.searchText);
        } else if (this.searchMode === 'id') {
            this.fetchByShowId(this.searchText);
        }
    }

    fetchByName(showName) {
        const self = this;
        if (showName) {
            this.dataFetchInProgress = true;
            this.myServiceService.getData(showName).subscribe((res: any) => {
                if (res.show_data && res.show_data.length) {
                    self.allShowData = res.show_data;
                    self.renderChart(self.allShowData, true);
                } else if (res.show_data && res.show_data.length === 0) {
                    this.errorMessage = 'Show not found';
                }
                if (res.recents) {
                    this.recents = res.recents.map(i => JSON.parse(i));
                }
                this.dataFetchInProgress = false;
            }, (err: any) => {
                this.errorMessage = err && err.error && err.error ? err.error.error : err;
                this.dataFetchInProgress = false;
            });
        }
    }

    fetchByShowId(showId: string): void {
        const self = this;
        if (showId) {
            this.dataFetchInProgress = true;
            this.myServiceService.getDataByImdbId(showId).subscribe((res: any) => {
                if (res.show_data && res.show_data.length) {
                    self.allShowData = res.show_data;
                    self.renderChart(self.allShowData, true);
                } else if (res.show_data && res.show_data.length === 0) {
                    this.errorMessage = 'Show not found';
                }
                if (res.recents) {
                    this.recents = res.recents.map(i => JSON.parse(i));
                }
                this.dataFetchInProgress = false;
            }, (err: any) => {
                this.errorMessage = err && err.error && err.error ? err.error.error : err;
                this.dataFetchInProgress = false;
            });
        }
    }

    fetchViaPoster(showId: string): void {
        this.searchMode = 'id';
        this.searchText = showId;
        this.fetchByShowId(showId);
    }

    fetchRecentsOnly(): void {
        this.myServiceService.getRecentsOnly().subscribe((res: any) => {
            this.recents = res.map(i => JSON.parse(i));
        }, (err) => {
            console.log('Error getting recents', err);
        });
    }

    renderChart(data, firstRender?: boolean): void {
        const self = this;
        for (let i = self.currentSeasons; i >= 0; i--) {
            self.chart.removeSerie(i);
        }
        if (data.length) {
            self.chart.ref.setTitle({text: data[0].name});
        }
        let ct = 0;
        const seasonMap: any = {};
        data.forEach((episode: any) => {
            if (!seasonMap[episode.season]) {
                seasonMap[episode.season] = [];
            }
            seasonMap[episode.season].push(episode);
        });
        self.currentSeasons = Object.keys(seasonMap).length;
        if (firstRender) {
            self.showSeasonsLengthArr = Array(Object.keys(seasonMap).length);
        }
        // this.zoomYAxis = false;
        // this.chart.ref.yAxis[0].setExtremes(0, 10, true, true);

        Object.keys(seasonMap).forEach((season: any) => {
            const showChartData = seasonMap[season].map((episode) => {
                episode.seriesNumber = self.formatSeriesNumber(episode);
                return {
                    x: ++ct,
                    y: episode.rating,
                    episode: episode
                };
            });
            self.chart.addSerie({
                name: `Season ${season}`,
                data: showChartData,
                marker: {
                    fillColor: self.findColor(season - 1),
                    symbol: 'circle'
                }
            });
        });
    }
}
