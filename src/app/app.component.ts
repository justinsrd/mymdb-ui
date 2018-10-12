import {Component} from '@angular/core';
import {Chart} from 'angular-highcharts';
import {MyServiceService} from './my-service.service';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss'],
    providers: [MyServiceService]
})
export class AppComponent {
    public title: string = 'firefly';
    private currentSeasons: number;
    public chart: any = new Chart({
        chart: {
            type: 'scatter',
            animation: true,
            backgroundColor: '#333333'
        },
        xAxis: {
            visible: false,
            tickWidth: 0
        },
        yAxis: {
            gridLineColor: '#424242'
        },
        legend: {
            enabled: false
        },
        title: {
            text: 'WHAT',
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
                console.log(this);
                /**
                     "episode": 1,
                     "episode_id": "tt0579539",
                     "episode_title": "The Train Job",
                     "id": 16531891,
                     "imdb_id": "tt0303461",
                     "name": "Firefly",
                     "rating": 8.5,
                     "season": 1,
                     "show_id": "tt0303461",
                     "votes": 3656
                 */
                const episode = this.point.episode;
                return `
                    <div class="tooltip-container">
                        <p class="episode-title font-weight-bold">${episode.episode_title}</p>
                        <p class="episode-number">${episode.seriesNumber}</p>
                        <p class="episode-rating">Rating: <span class="value font-weight-bold">${Number(episode.rating).toFixed(1)}</span></p>
                        <p class="episode-votes">Votes: </span class="value">${episode.votes}</span></p>
                    </div>
                `;
            }
        }
    });

    constructor(private myServiceService: MyServiceService) {

    }

    findColor(index: number) {
        // season 6, of 8 seasons


        // season 13, of 30 seasons
        const colors = ['#7ed1f0', '#f1ef85', '#cb78ed', '#7ff2ad', '#ef857c', '#7b8eed', '#b5f284', '#f079d3', '#80f2ea'];
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


    fetchStuff() {
        const self = this;
        console.log('str2', this.title);
        const colors = ['#2f7ed8', '#0d233a', '#8bbc21', '#910000', '#1aadce', '#492970', '#f28f43', '#77a1e5', '#c42525', '#a6c96a'];

        if (this.title) {
            this.myServiceService.getData(this.title).subscribe((res: any) => {
                console.log('res', res);
                // const data = res.map((episode: any) => {
                //     return episode.rating;
                // });
                console.log('this chart', self.chart);

                for (let i = self.currentSeasons; i >= 0; i--) {
                    console.log('removed', i);
                    self.chart.removeSerie(i);
                }

                if (res.length) {
                    self.chart.ref.setTitle({text: res[0].name});
                }


                // self.chart.removeSerie(0);
                //
                // const data = res.map((episode: any) => {
                //     console.log(typeof episode.season, episode.season);
                //     return {
                //         x: 7,
                //         y: episode.rating,
                //         color: colors[episode.season - 1] || '#f00'
                //     }
                // });
                let ct = 0;
                const seasonMap: any = {};
                res.forEach((episode: any) => {
                    if (!seasonMap[episode.season]) {
                        seasonMap[episode.season] = [];
                    }
                    seasonMap[episode.season].push(episode);
                });
                self.currentSeasons = Object.keys(seasonMap).length;

                Object.keys(seasonMap).forEach((season: any) => {
                    console.log('season', season);
                    const data = seasonMap[season].map((episode) => {
                        episode.seriesNumber = self.formatSeriesNumber(episode);
                        return  {
                            x: ++ct,
                            y: episode.rating,
                            color: colors[season],
                            episode: episode
                        }
                    });
                    self.chart.addSerie({
                        name: `Season ${season}`,
                        data: data,
                        marker: {
                            // fillColor: colors[season] || '#f00',
                            fillColor: self.findColor(season - 1),
                            symbol: 'circle'
                        },
                        // tooltip: {
                        //     headerFormat: 'meow'
                        // }
                        // tooltip: {
                        //     formatter: function() {
                        //         return '';
                        //     }
                        // }
                    });
                });
                // console.log('data', data);
                // this.chart.addSerie({
                //     name: 'Stuff',
                //     data: data,
                //     marker: {
                //         symbol: 'circle'
                //     }
                // });








                // this.chart.addSerie({name: this.title, data: data});
                console.log('seasonMap', seasonMap);
            }, (err: any) => {
                console.log('err', err);
            });
        }
    }
}
