import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, catchError, map } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Schedule, ScheduleCreateDto, ScheduleUpdateDto } from '../models/schedule.model';

@Injectable({
  providedIn: 'root'
})
export class ScheduleService {
  private apiUrl = `${environment.apiUrl}/schedules/`;

  constructor(private http: HttpClient) {}

  getSchedules(): Observable<Schedule[]> {
    return this.http.get<Schedule[]>(this.apiUrl).pipe(
      map(data => Array.isArray(data) ? data : []),
      catchError(error => {
        console.error('Error fetching schedules:', error);
        return of([]); // Return empty array on error
      })
    );
  }

  getSchedule(id: number): Observable<Schedule> {
    return this.http.get<Schedule>(`${this.apiUrl}${id}`);
  }

  createSchedule(schedule: ScheduleCreateDto): Observable<Schedule> {
    return this.http.post<Schedule>(this.apiUrl, schedule);
  }

  updateSchedule(id: number, schedule: ScheduleUpdateDto): Observable<Schedule> {
    return this.http.put<Schedule>(`${this.apiUrl}${id}`, schedule);
  }

  deleteSchedule(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}${id}`);
  }
}
