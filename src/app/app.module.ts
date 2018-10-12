import {BrowserModule} from '@angular/platform-browser';
import {NgModule} from '@angular/core';

import {AppComponent} from './app.component';
import {ChartModule} from 'angular-highcharts';
import {FormsModule} from '@angular/forms';
import {MyServiceService} from './my-service.service';
import {HttpClientModule} from '@angular/common/http';

@NgModule({
    declarations: [
        AppComponent
    ],
    imports: [
        BrowserModule,
        ChartModule,
        FormsModule,
        HttpClientModule
    ],
    providers: [
        MyServiceService
    ],
    bootstrap: [AppComponent]
})
export class AppModule {
}
