import { Component, OnInit } from '@angular/core';
import { Schedule } from '../../shared/models/schedule.model';
import { Consumable } from '../../shared/models/consumable.model';
import { ScheduleService } from '../../shared/services/schedule.service';
import { ConsumableService } from '../../shared/services/consumable.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  schedules: Schedule[] = [];
  consumables: Consumable[] = [];
  isLoadingSchedules = true;
  isLoadingConsumables = true;
  error: string | null = null;

  constructor(
    private scheduleService: ScheduleService,
    private consumableService: ConsumableService
  ) {}

  ngOnInit(): void {
    this.loadDashboardData();
  }

  loadDashboardData(): void {
    this.isLoadingSchedules = true;
    this.isLoadingConsumables = true;
    
    this.scheduleService.getSchedules().subscribe({
      next: (data) => {
        this.schedules = data;
        this.isLoadingSchedules = false;
      },
      error: (error) => {
        console.error('Error loading schedules', error);
        this.error = '無法載入行事曆資料';
        this.isLoadingSchedules = false;
      }
    });

    this.consumableService.getConsumables().subscribe({
      next: (data) => {
        this.consumables = data;
        this.isLoadingConsumables = false;
      },
      error: (error) => {
        console.error('Error loading consumables', error);
        this.error = '無法載入耗材資料';
        this.isLoadingConsumables = false;
      }
    });
  }
}
