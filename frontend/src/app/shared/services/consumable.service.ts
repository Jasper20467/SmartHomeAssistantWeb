import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Consumable, ConsumableCreateDto, ConsumableUpdateDto } from '../models/consumable.model';

@Injectable({
  providedIn: 'root'
})
export class ConsumableService {
  private apiUrl = `${environment.apiUrl}/consumables/`;

  constructor(private http: HttpClient) {}

  getConsumables(): Observable<Consumable[]> {
    return this.http.get<Consumable[]>(this.apiUrl);
  }

  getConsumable(id: number): Observable<Consumable> {
    return this.http.get<Consumable>(`${this.apiUrl}${id}`);
  }

  createConsumable(consumable: ConsumableCreateDto): Observable<Consumable> {
    return this.http.post<Consumable>(this.apiUrl, consumable);
  }

  updateConsumable(id: number, consumable: ConsumableUpdateDto): Observable<Consumable> {
    return this.http.put<Consumable>(`${this.apiUrl}${id}`, consumable);
  }

  deleteConsumable(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}${id}`);
  }
}
