import { Component, OnInit, Input, Output, EventEmitter, OnChanges, SimpleChanges, ViewEncapsulation } from '@angular/core';
import { Schedule } from '../../models/schedule.model';

interface CalendarDate {
  date: Date;
  isCurrentMonth: boolean;
  isToday: boolean;
  isSelected: boolean;
  schedules: Schedule[];
}

@Component({
  selector: 'app-calendar',
  templateUrl: './calendar.component.html',
  styleUrls: ['./calendar.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class CalendarComponent implements OnInit, OnChanges {
  @Input() schedules: Schedule[] = [];
  @Output() dateSelected = new EventEmitter<Date>();
  @Output() scheduleClicked = new EventEmitter<Schedule>();

  currentDate = new Date();
  selectedDate: Date | null = null;
  calendarDates: CalendarDate[] = [];

  monthNames = [
    '一月', '二月', '三月', '四月', '五月', '六月',
    '七月', '八月', '九月', '十月', '十一月', '十二月'
  ];

  dayNames = ['日', '一', '二', '三', '四', '五', '六'];

  ngOnInit() {
    // 確保 schedules 是陣列
    if (!this.schedules || !Array.isArray(this.schedules)) {
      this.schedules = [];
    }
    
    // 設定預設選中日期為今天
    this.selectedDate = new Date();
    this.generateCalendar();
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['schedules']) {
      // 確保 schedules 是陣列
      if (!this.schedules || !Array.isArray(this.schedules)) {
        this.schedules = [];
      }
      this.generateCalendar();
    }
  }

  generateCalendar() {
    const year = this.currentDate.getFullYear();
    const month = this.currentDate.getMonth();
    
    // Get first day of month and last day of month
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    
    // Get first day of calendar (might be from previous month)
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());
    
    // Get last day of calendar (might be from next month)
    const endDate = new Date(lastDay);
    endDate.setDate(endDate.getDate() + (6 - lastDay.getDay()));
    
    this.calendarDates = [];
    const currentDay = new Date(startDate);
    
    while (currentDay <= endDate) {
      const dateSchedules = this.getSchedulesForDate(currentDay);
      
      this.calendarDates.push({
        date: new Date(currentDay),
        isCurrentMonth: currentDay.getMonth() === month,
        isToday: this.isToday(currentDay),
        isSelected: this.isSelectedDate(currentDay),
        schedules: dateSchedules
      });
      
      currentDay.setDate(currentDay.getDate() + 1);
    }
  }

  getSchedulesForDate(date: Date): Schedule[] {
    // 確保 schedules 是陣列
    if (!this.schedules || !Array.isArray(this.schedules)) {
      return [];
    }
    
    return this.schedules.filter(schedule => {
      if (!schedule || !schedule.start_time) {
        return false;
      }
      const scheduleDate = new Date(schedule.start_time);
      return this.isSameDay(scheduleDate, date);
    });
  }

  isToday(date: Date): boolean {
    const today = new Date();
    return this.isSameDay(date, today);
  }

  isSelectedDate(date: Date): boolean {
    return this.selectedDate ? this.isSameDay(date, this.selectedDate) : false;
  }

  isSameDay(date1: Date, date2: Date): boolean {
    return date1.getFullYear() === date2.getFullYear() &&
           date1.getMonth() === date2.getMonth() &&
           date1.getDate() === date2.getDate();
  }

  onDateClick(calendarDate: CalendarDate) {
    this.selectedDate = calendarDate.date;
    this.generateCalendar(); // Regenerate to update selected state
    this.dateSelected.emit(calendarDate.date);
  }

  onScheduleClick(schedule: Schedule, event: Event) {
    event.stopPropagation();
    this.scheduleClicked.emit(schedule);
  }

  previousMonth() {
    this.currentDate.setMonth(this.currentDate.getMonth() - 1);
    this.generateCalendar();
  }

  nextMonth() {
    this.currentDate.setMonth(this.currentDate.getMonth() + 1);
    this.generateCalendar();
  }

  goToToday() {
    this.currentDate = new Date();
    this.selectedDate = new Date();
    this.generateCalendar();
  }

  get currentMonthYear(): string {
    return `${this.currentDate.getFullYear()}年 ${this.monthNames[this.currentDate.getMonth()]}`;
  }
}
