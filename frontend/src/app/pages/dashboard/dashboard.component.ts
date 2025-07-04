import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
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
  selectedDate: Date | null = null;
  selectedDateSchedules: Schedule[] = [];

  constructor(
    private scheduleService: ScheduleService,
    private consumableService: ConsumableService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadDashboardData();
    // Set today as default selected date
    this.selectedDate = new Date();
    this.updateSelectedDateSchedules();
  }
  
  private updateSelectedDateSchedules(): void {
    if (this.selectedDate) {
      this.selectedDateSchedules = this.schedules.filter(schedule => {
        const scheduleDate = new Date(schedule.start_time);
        return this.isSameDay(scheduleDate, this.selectedDate!);
      });
    }
  }

  loadDashboardData(): void {
    this.isLoadingSchedules = true;
    this.isLoadingConsumables = true;
    
    this.scheduleService.getSchedules().subscribe({
      next: (data) => {
        this.schedules = data || []; // Ensure it's always an array
        this.isLoadingSchedules = false;
        this.updateSelectedDateSchedules(); // Update selected date schedules after loading
      },
      error: (error) => {
        console.error('Error loading schedules', error);
        this.error = '無法載入行事曆資料';
        this.schedules = []; // Set empty array on error
        this.isLoadingSchedules = false;
        this.updateSelectedDateSchedules(); // Update even on error
      }
    });

    this.consumableService.getConsumables().subscribe({
      next: (data) => {
        this.consumables = data || []; // Ensure it's always an array
        this.isLoadingConsumables = false;
      },
      error: (error) => {
        console.error('Error loading consumables', error);
        this.error = '無法載入耗材資料';
        this.consumables = []; // Set empty array on error
        this.isLoadingConsumables = false;
      }
    });
  }

  onDateSelected(date: Date): void {
    this.selectedDate = date;
    this.updateSelectedDateSchedules();
  }

  onScheduleClicked(schedule: Schedule): void {
    // Navigate to schedule page and edit the schedule
    this.router.navigate(['/schedule'], { 
      queryParams: { 
        edit: schedule.id 
      } 
    });
  }

  private isSameDay(date1: Date, date2: Date): boolean {
    return date1.getFullYear() === date2.getFullYear() &&
           date1.getMonth() === date2.getMonth() &&
           date1.getDate() === date2.getDate();
  }
}
