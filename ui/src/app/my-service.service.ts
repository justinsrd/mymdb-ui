import {Injectable} from '@angular/core';
import {HttpClient, HttpParams} from '@angular/common/http';
import {environment} from '../environments/environment';

@Injectable({
    providedIn: 'root'
})
export class MyServiceService {

    constructor(private http: HttpClient) {

    }

    getData(title: string) {
        const params: any = new HttpParams({
            fromObject: {
                title: title
            }
        });
        return this.http.get(environment.mymdbApiDomain, {params: params});
    }

    getDataByImdbId(imdbId: string) {
        const params: any = new HttpParams({
            fromObject: {
                imdb_id: imdbId
            }
        });
        return this.http.get(environment.mymdbApiDomain, {params: params});
    }
}
