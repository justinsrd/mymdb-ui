import {Injectable} from '@angular/core';
import {HttpClient, HttpParams} from '@angular/common/http';

@Injectable({
    providedIn: 'root'
})
export class MyServiceService {

    constructor(private http: HttpClient) {

    }

    getData(title: string) {
        const url = 'http://localhost:5000';

        const params: any = new HttpParams({
            fromObject: {
                title: title
            }
        });
        return this.http.get(url, {params: params});
    }
}
