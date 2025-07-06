import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { Schedule, ScheduleCreateDto } from '../../shared/models/schedule.model';
import { ScheduleService } from '../../shared/services/schedule.service';

@Component({
  selector: 'app-schedule',
  templateUrl: './schedule.component.html',
  styleUrls: ['./schedule.component.scss']
})
export class ScheduleComponent implements OnInit {
  schedules: Schedule[] = [];
  scheduleForm: FormGroup;
  isLoading = true;
  isSubmitting = false;
  editingScheduleId: number | null = null;
  showForm = false;
  error: string | null = null;
  isCalendarView = true; // Default to calendar view
  selectedDate: Date | null = null;
  selectedDateSchedules: Schedule[] = [];
  
  // Hours array for dropdown (0-23)
  hours: number[] = Array.from({length: 24}, (_, i) => i);

  constructor(
    private scheduleService: ScheduleService,
    private fb: FormBuilder,
    private route: ActivatedRoute
  ) {
    this.scheduleForm = this.fb.group({
      title: ['', [Validators.required]],
      description: [''],
      start_time: ['', [Validators.required, this.timeIntervalValidator]],
      end_time: ['', [this.timeIntervalValidator]]
    }, { validators: this.endTimeAfterStartTimeValidator });
  }

  ngOnInit(): void {
    this.loadSchedules();
  }

  loadSchedules(): void {
    this.isLoading = true;
    this.scheduleService.getSchedules().subscribe({
      next: (data) => {
        this.schedules = data || []; // Ensure it's always an array
        this.isLoading = false;
        
        // Check for edit parameter from dashboard after schedules are loaded
        this.route.queryParams.subscribe(params => {
          if (params['edit']) {
            const scheduleId = parseInt(params['edit']);
            const schedule = this.schedules.find(s => s.id === scheduleId);
            if (schedule) {
              this.editSchedule(schedule);
            }
          }
        });
      },
      error: (error) => {
        console.error('Error loading schedules', error);
        this.error = '無法載入行事曆資料';
        this.schedules = []; // Set empty array on error
        this.isLoading = false;
      }
    });
  }

  onSubmit(): void {
    if (this.scheduleForm.invalid) {
      return;
    }

    this.isSubmitting = true;
    const formData = this.scheduleForm.value;

    // Ensure description is always a string
    const scheduleData: ScheduleCreateDto = {
      title: formData.title,
      description: formData.description || "", // Default to an empty string
      start_time: new Date(formData.start_time).toISOString(),
      end_time: formData.end_time ? new Date(formData.end_time).toISOString() : undefined
    };

    if (this.editingScheduleId) {
      this.scheduleService.updateSchedule(this.editingScheduleId, scheduleData).subscribe({
        next: () => {
          this.resetForm();
          this.loadSchedules();
        },
        error: (error) => {
          console.error('Error updating schedule', error);
          this.error = '更新行程失敗';
          this.isSubmitting = false;
        }
      });
    } else {
      this.scheduleService.createSchedule(scheduleData).subscribe({
        next: () => {
          this.resetForm();
          this.loadSchedules();
        },
        error: (error) => {
          console.error('Error creating schedule', error);
          this.error = '新增行程失敗';
          this.isSubmitting = false;
        }
      });
    }
  }

  editSchedule(schedule: Schedule): void {
    if (schedule.id) {
      this.editingScheduleId = schedule.id;
      this.showForm = true;
      
      // Prepare dates for form input (HTML input expects YYYY-MM-DDThh:mm format)
      const startTime = new Date(schedule.start_time);
      const endTime = schedule.end_time ? new Date(schedule.end_time) : null;
      
      // Round times to nearest 30 minutes for consistency
      const roundedStartTime = this.roundToNearestHalfHour(startTime.toISOString().slice(0, 16));
      const roundedEndTime = endTime ? this.roundToNearestHalfHour(endTime.toISOString().slice(0, 16)) : '';
      
      this.scheduleForm.patchValue({
        title: schedule.title,
        description: schedule.description,
        start_time: roundedStartTime,
        end_time: roundedEndTime
      });
    }
  }

  deleteSchedule(id: number): void {
    if (confirm('確定要刪除此行程嗎?')) {
      this.scheduleService.deleteSchedule(id).subscribe({
        next: () => {
          this.loadSchedules();
        },
        error: (error) => {
          console.error('Error deleting schedule', error);
          this.error = '刪除行程失敗';
        }
      });
    }
  }

  resetForm(): void {
    this.scheduleForm.reset();
    this.editingScheduleId = null;
    this.isSubmitting = false;
    this.showForm = false;
  }

  toggleForm(): void {
    if (this.showForm) {
      this.resetForm();
    } else {
      this.showForm = true;
      
      // Set default times when creating new schedule
      if (!this.editingScheduleId) {
        this.setDefaultTimes();
      }
    }
  }

  // Set default times to nearest half hour
  private setDefaultTimes(): void {
    const now = new Date();
    
    // Round current time to next half hour
    const currentMinutes = now.getMinutes();
    if (currentMinutes <= 30) {
      now.setMinutes(30);
    } else {
      now.setMinutes(0);
      now.setHours(now.getHours() + 1);
    }
    now.setSeconds(0);
    now.setMilliseconds(0);
    
    const startTime = now.toISOString().slice(0, 16);
    
    // Set end time to 1 hour after start time
    const endTime = new Date(now);
    endTime.setHours(endTime.getHours() + 1);
    const endTimeString = endTime.toISOString().slice(0, 16);
    
    this.scheduleForm.patchValue({
      start_time: startTime,
      end_time: endTimeString
    });
  }

  toggleView(): void {
    this.isCalendarView = !this.isCalendarView;
  }

  onDateSelected(date: Date): void {
    this.selectedDate = date;
    this.selectedDateSchedules = this.schedules.filter(schedule => {
      const scheduleDate = new Date(schedule.start_time);
      return this.isSameDay(scheduleDate, date);
    });
    
    // Auto-fill form with selected date if adding new schedule
    if (this.showForm && !this.editingScheduleId) {
      const selectedDateTime = new Date(date);
      
      // Set to next available half hour
      const now = new Date();
      const currentMinutes = now.getMinutes();
      
      if (currentMinutes <= 30) {
        selectedDateTime.setHours(now.getHours(), 30, 0, 0);
      } else {
        selectedDateTime.setHours(now.getHours() + 1, 0, 0, 0);
      }
      
      // If selected date is different from today, default to 9:00 AM
      if (!this.isSameDay(date, now)) {
        selectedDateTime.setHours(9, 0, 0, 0);
      }
      
      const endDateTime = new Date(selectedDateTime);
      endDateTime.setHours(endDateTime.getHours() + 1);
      
      this.scheduleForm.patchValue({
        start_time: this.formatDateForInput(selectedDateTime),
        end_time: this.formatDateForInput(endDateTime)
      });
    }
  }

  onScheduleClicked(schedule: Schedule): void {
    this.editSchedule(schedule);
  }

  private isSameDay(date1: Date, date2: Date): boolean {
    return date1.getFullYear() === date2.getFullYear() &&
           date1.getMonth() === date2.getMonth() &&
           date1.getDate() === date2.getDate();
  }

  // Helper to format date for datetime-local input
  private formatDateForInput(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  }

  // Custom validator to ensure time intervals are 30 minutes (00 or 30 only)
  private timeIntervalValidator(control: AbstractControl): ValidationErrors | null {
    if (!control.value) {
      return null;
    }
    
    const dateTime = new Date(control.value);
    const minutes = dateTime.getMinutes();
    
    if (minutes !== 0 && minutes !== 30) {
      return { timeInterval: '請選擇整點或半點時間（例如：09:00 或 09:30）' };
    }
    
    return null;
  }

  // Custom validator to ensure end time is after start time
  private endTimeAfterStartTimeValidator(formGroup: AbstractControl): ValidationErrors | null {
    const startTime = formGroup.get('start_time')?.value;
    const endTime = formGroup.get('end_time')?.value;
    
    if (!startTime || !endTime) {
      return null; // Don't validate if either is empty
    }
    
    const startDate = new Date(startTime);
    const endDate = new Date(endTime);
    
    if (endDate <= startDate) {
      return { endTimeBeforeStart: '結束時間必須晚於開始時間' };
    }
    
    return null;
  }

  // Helper to round time to nearest 30 minutes (00 or 30 only)
  private roundToNearestHalfHour(dateTimeString: string): string {
    const date = new Date(dateTimeString);
    const minutes = date.getMinutes();
    
    // Force to 00 or 30 minutes only
    if (minutes <= 15) {
      date.setMinutes(0);
    } else if (minutes <= 45) {
      date.setMinutes(30);
    } else {
      date.setMinutes(0);
      date.setHours(date.getHours() + 1);
    }
    
    date.setSeconds(0);
    date.setMilliseconds(0);
    
    return date.toISOString().slice(0, 16);
  }

  // Get minimum end time based on start time (at least 30 minutes after start)
  getMinEndTime(): string {
    const startTime = this.scheduleForm.get('start_time')?.value;
    if (!startTime) {
      return '';
    }
    
    const startDate = new Date(startTime);
    startDate.setMinutes(startDate.getMinutes() + 30);
    
    return startDate.toISOString().slice(0, 16);
  }

  // Handle start time blur event to round to nearest 30 minutes
  onStartTimeBlur(): void {
    const startTimeControl = this.scheduleForm.get('start_time');
    if (startTimeControl?.value) {
      const roundedTime = this.roundToNearestHalfHour(startTimeControl.value);
      startTimeControl.setValue(roundedTime);
      
      // Update end time min constraint
      const endTimeControl = this.scheduleForm.get('end_time');
      if (endTimeControl?.value) {
        const endTime = new Date(endTimeControl.value);
        const startTime = new Date(roundedTime);
        
        // If end time is now before start time, adjust it
        if (endTime <= startTime) {
          const newEndTime = new Date(startTime);
          newEndTime.setMinutes(newEndTime.getMinutes() + 30);
          endTimeControl.setValue(newEndTime.toISOString().slice(0, 16));
        }
      }
    }
  }

  // Handle end time blur event to round to nearest 30 minutes
  onEndTimeBlur(): void {
    const endTimeControl = this.scheduleForm.get('end_time');
    if (endTimeControl?.value) {
      const roundedTime = this.roundToNearestHalfHour(endTimeControl.value);
      endTimeControl.setValue(roundedTime);
      
      // Ensure end time is still after start time
      const startTime = this.scheduleForm.get('start_time')?.value;
      if (startTime) {
        const startDate = new Date(startTime);
        const endDate = new Date(roundedTime);
        
        if (endDate <= startDate) {
          const newEndTime = new Date(startDate);
          newEndTime.setMinutes(newEndTime.getMinutes() + 30);
          endTimeControl.setValue(newEndTime.toISOString().slice(0, 16));
        }
      }
    }
  }

  // Handle time input change to enforce 30-minute intervals
  onStartTimeChange(event: any): void {
    const value = event.target.value;
    if (value) {
      const roundedTime = this.roundToNearestHalfHour(value);
      this.scheduleForm.get('start_time')?.setValue(roundedTime, { emitEvent: false });
    }
  }

  // Handle end time input change to enforce 30-minute intervals
  onEndTimeChange(event: any): void {
    const value = event.target.value;
    if (value) {
      const roundedTime = this.roundToNearestHalfHour(value);
      this.scheduleForm.get('end_time')?.setValue(roundedTime, { emitEvent: false });
      
      // Ensure end time is still after start time
      const startTime = this.scheduleForm.get('start_time')?.value;
      if (startTime) {
        const startDate = new Date(startTime);
        const endDate = new Date(roundedTime);
        
        if (endDate <= startDate) {
          const newEndTime = new Date(startDate);
          newEndTime.setMinutes(newEndTime.getMinutes() + 30);
          this.scheduleForm.get('end_time')?.setValue(newEndTime.toISOString().slice(0, 16), { emitEvent: false });
        }
      }
    }
  }

  // Enhanced input event handler for strict minute control
  onTimeInput(event: any, isStartTime: boolean = true): void {
    const input = event.target;
    const value = input.value;
    
    if (value && value.length >= 16) { // Full datetime-local format
      const date = new Date(value);
      const minutes = date.getMinutes();
      
      // Force to 00 or 30 minutes immediately
      if (minutes !== 0 && minutes !== 30) {
        const roundedTime = this.roundToNearestHalfHour(value);
        
        if (isStartTime) {
          this.scheduleForm.get('start_time')?.setValue(roundedTime, { emitEvent: false });
        } else {
          this.scheduleForm.get('end_time')?.setValue(roundedTime, { emitEvent: false });
        }
        
        // Update the input value directly
        input.value = roundedTime;
      }
    }
  }

  // Enhanced keyboard event handler to restrict minute inputs more strictly
  onTimeKeydown(event: KeyboardEvent): void {
    const input = event.target as HTMLInputElement;
    const value = input.value;
    const selectionStart = input.selectionStart || 0;
    const key = event.key;
    
    // Allow navigation and control keys
    if (['Backspace', 'Delete', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Tab', 'Enter', 'Escape'].includes(key)) {
      return;
    }
    
    // Allow Ctrl+A, Ctrl+C, Ctrl+V, Ctrl+X
    if (event.ctrlKey && ['a', 'c', 'v', 'x'].includes(key.toLowerCase())) {
      return;
    }
    
    // Check if we're in the minutes section (positions 14-15 in YYYY-MM-DDTHH:MM)
    if (selectionStart >= 14 && selectionStart <= 15) {
      // For minute input, only allow specific combinations
      if (selectionStart === 14) {
        // First digit of minutes: only allow 0, 3
        if (!['0', '3'].includes(key)) {
          event.preventDefault();
          return;
        }
      } else if (selectionStart === 15) {
        // Second digit of minutes
        const firstMinuteDigit = value.charAt(14);
        if (firstMinuteDigit === '0' && key !== '0') {
          event.preventDefault(); // Only 00 allowed
          return;
        } else if (firstMinuteDigit === '3' && key !== '0') {
          event.preventDefault(); // Only 30 allowed
          return;
        }
      }
    }
    
    // For other positions, allow numeric input
    if (!/[0-9]/.test(key)) {
      event.preventDefault();
    }
  }

  // ===== Custom DateTime Picker Methods =====
  
  // Get start date value for date input
  getStartDate(): string {
    const startTime = this.scheduleForm.get('start_time')?.value;
    if (!startTime) return '';
    
    try {
      const date = new Date(startTime);
      if (isNaN(date.getTime())) return '';
      
      // 使用本地時區格式化，避免時區轉換問題
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      
      return `${year}-${month}-${day}`;
    } catch (error) {
      console.error('Error parsing start date:', error);
      return '';
    }
  }
  
  // Get start hour value for hour select
  getStartHour(): string {
    const startTime = this.scheduleForm.get('start_time')?.value;
    if (!startTime) return '';
    
    try {
      const date = new Date(startTime);
      if (isNaN(date.getTime())) return '';
      
      return date.getHours().toString();
    } catch (error) {
      console.error('Error parsing start hour:', error);
      return '';
    }
  }
  
  // Get start minute value for minute select
  getStartMinute(): string {
    const startTime = this.scheduleForm.get('start_time')?.value;
    if (!startTime) return '';
    
    try {
      const date = new Date(startTime);
      if (isNaN(date.getTime())) return '';
      
      return date.getMinutes().toString();
    } catch (error) {
      console.error('Error parsing start minute:', error);
      return '';
    }
  }
  
  // Get end date value for date input
  getEndDate(): string {
    const endTime = this.scheduleForm.get('end_time')?.value;
    if (!endTime) return '';
    
    try {
      const date = new Date(endTime);
      if (isNaN(date.getTime())) return '';
      
      // 使用本地時區格式化，避免時區轉換問題
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      
      return `${year}-${month}-${day}`;
    } catch (error) {
      console.error('Error parsing end date:', error);
      return '';
    }
  }
  
  // Get end hour value for hour select
  getEndHour(): string {
    const endTime = this.scheduleForm.get('end_time')?.value;
    if (!endTime) return '';
    
    try {
      const date = new Date(endTime);
      if (isNaN(date.getTime())) return '';
      
      return date.getHours().toString();
    } catch (error) {
      console.error('Error parsing end hour:', error);
      return '';
    }
  }
  
  // Get end minute value for minute select
  getEndMinute(): string {
    const endTime = this.scheduleForm.get('end_time')?.value;
    if (!endTime) return '';
    
    try {
      const date = new Date(endTime);
      if (isNaN(date.getTime())) return '';
      
      return date.getMinutes().toString();
    } catch (error) {
      console.error('Error parsing end minute:', error);
      return '';
    }
  }
  
  // Handle start date change
  onStartDateChange(event: any): void {
    const dateValue = event.target.value;
    if (!dateValue) return;
    
    const currentStartTime = this.scheduleForm.get('start_time')?.value;
    let hour = 9; // Default to 9 AM
    let minute = 0; // Default to 00
    
    if (currentStartTime) {
      try {
        const currentDate = new Date(currentStartTime);
        if (!isNaN(currentDate.getTime())) {
          hour = currentDate.getHours();
          minute = currentDate.getMinutes();
        }
      } catch (error) {
        console.error('Error parsing current start time:', error);
      }
    }
    
    // 直接使用 Date 構造函數創建日期，避免時區問題
    const [year, month, day] = dateValue.split('-');
    const newDateTime = new Date(parseInt(year), parseInt(month) - 1, parseInt(day), hour, minute, 0, 0);
    
    // 使用本地時間格式設置表單值
    const formattedDateTime = this.formatDateForInput(newDateTime);
    this.scheduleForm.get('start_time')?.setValue(formattedDateTime);
    this.validateAndUpdateEndTime();
  }
  
  // Handle start hour change
  onStartHourChange(event: any): void {
    const hourValue = parseInt(event.target.value);
    if (isNaN(hourValue)) return;
    
    const currentStartTime = this.scheduleForm.get('start_time')?.value;
    let date = new Date();
    let minute = 0;
    
    if (currentStartTime) {
      try {
        date = new Date(currentStartTime);
        if (!isNaN(date.getTime())) {
          minute = date.getMinutes();
        } else {
          date = new Date();
        }
      } catch (error) {
        console.error('Error parsing current start time:', error);
        date = new Date();
      }
    }
    
    date.setHours(hourValue, minute, 0, 0);
    
    const formattedDateTime = this.formatDateForInput(date);
    this.scheduleForm.get('start_time')?.setValue(formattedDateTime);
    this.validateAndUpdateEndTime();
  }
  
  // Handle start minute change
  onStartMinuteChange(event: any): void {
    const minuteValue = parseInt(event.target.value);
    if (isNaN(minuteValue)) return;
    
    const currentStartTime = this.scheduleForm.get('start_time')?.value;
    let date = new Date();
    
    if (currentStartTime) {
      try {
        date = new Date(currentStartTime);
        if (isNaN(date.getTime())) {
          date = new Date();
        }
      } catch (error) {
        console.error('Error parsing current start time:', error);
        date = new Date();
      }
    }
    
    date.setMinutes(minuteValue, 0, 0);
    
    const formattedDateTime = this.formatDateForInput(date);
    this.scheduleForm.get('start_time')?.setValue(formattedDateTime);
    this.validateAndUpdateEndTime();
  }
  
  // Handle end date change
  onEndDateChange(event: any): void {
    const dateValue = event.target.value;
    if (!dateValue) return;
    
    const currentEndTime = this.scheduleForm.get('end_time')?.value;
    let hour = 10; // Default to 10 AM
    let minute = 0; // Default to 00
    
    if (currentEndTime) {
      try {
        const currentDate = new Date(currentEndTime);
        if (!isNaN(currentDate.getTime())) {
          hour = currentDate.getHours();
          minute = currentDate.getMinutes();
        }
      } catch (error) {
        console.error('Error parsing current end time:', error);
      }
    }
    
    // 直接使用 Date 構造函數創建日期，避免時區問題
    const [year, month, day] = dateValue.split('-');
    const newDateTime = new Date(parseInt(year), parseInt(month) - 1, parseInt(day), hour, minute, 0, 0);
    
    // 使用本地時間格式設置表單值
    const formattedDateTime = this.formatDateForInput(newDateTime);
    this.scheduleForm.get('end_time')?.setValue(formattedDateTime);
    this.validateEndTimeAfterStart();
  }
  
  // Handle end hour change
  onEndHourChange(event: any): void {
    const hourValue = parseInt(event.target.value);
    if (isNaN(hourValue)) return;
    
    const currentEndTime = this.scheduleForm.get('end_time')?.value;
    let date = new Date();
    let minute = 0;
    
    if (currentEndTime) {
      try {
        date = new Date(currentEndTime);
        if (!isNaN(date.getTime())) {
          minute = date.getMinutes();
        } else {
          date = new Date();
        }
      } catch (error) {
        console.error('Error parsing current end time:', error);
        date = new Date();
      }
    }
    
    date.setHours(hourValue, minute, 0, 0);
    
    const formattedDateTime = this.formatDateForInput(date);
    this.scheduleForm.get('end_time')?.setValue(formattedDateTime);
    this.validateEndTimeAfterStart();
  }
  
  // Handle end minute change
  onEndMinuteChange(event: any): void {
    const minuteValue = parseInt(event.target.value);
    if (isNaN(minuteValue)) return;
    
    const currentEndTime = this.scheduleForm.get('end_time')?.value;
    let date = new Date();
    
    if (currentEndTime) {
      try {
        date = new Date(currentEndTime);
        if (isNaN(date.getTime())) {
          date = new Date();
        }
      } catch (error) {
        console.error('Error parsing current end time:', error);
        date = new Date();
      }
    }
    
    date.setMinutes(minuteValue, 0, 0);
    
    const formattedDateTime = this.formatDateForInput(date);
    this.scheduleForm.get('end_time')?.setValue(formattedDateTime);
    this.validateEndTimeAfterStart();
  }
  
  // Validate and update end time when start time changes
  private validateAndUpdateEndTime(): void {
    const startTime = this.scheduleForm.get('start_time')?.value;
    const endTime = this.scheduleForm.get('end_time')?.value;
    
    if (startTime && endTime) {
      const startDate = new Date(startTime);
      const endDate = new Date(endTime);
      
      // If end time is before or equal to start time, update it
      if (endDate <= startDate) {
        const newEndTime = new Date(startDate);
        newEndTime.setMinutes(newEndTime.getMinutes() + 30);
        this.scheduleForm.get('end_time')?.setValue(this.formatDateForInput(newEndTime));
      }
    } else if (startTime && !endTime) {
      // If no end time set, default to 1 hour after start
      const startDate = new Date(startTime);
      const defaultEndTime = new Date(startDate);
      defaultEndTime.setHours(defaultEndTime.getHours() + 1);
      this.scheduleForm.get('end_time')?.setValue(this.formatDateForInput(defaultEndTime));
    }
  }
  
  // Validate that end time is after start time
  private validateEndTimeAfterStart(): void {
    const startTime = this.scheduleForm.get('start_time')?.value;
    const endTime = this.scheduleForm.get('end_time')?.value;
    
    if (startTime && endTime) {
      const startDate = new Date(startTime);
      const endDate = new Date(endTime);
      
      // If end time is before or equal to start time, adjust it
      if (endDate <= startDate) {
        const newEndTime = new Date(startDate);
        newEndTime.setMinutes(newEndTime.getMinutes() + 30);
        this.scheduleForm.get('end_time')?.setValue(this.formatDateForInput(newEndTime));
      }
    }
  }
}
