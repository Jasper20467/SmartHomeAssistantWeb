import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
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

  constructor(
    private scheduleService: ScheduleService,
    private fb: FormBuilder
  ) {
    this.scheduleForm = this.fb.group({
      title: ['', [Validators.required]],
      description: [''],
      start_time: ['', [Validators.required]],
      end_time: ['']
    });
  }

  ngOnInit(): void {
    this.loadSchedules();
  }

  loadSchedules(): void {
    this.isLoading = true;
    this.scheduleService.getSchedules().subscribe({
      next: (data) => {
        this.schedules = data;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading schedules', error);
        this.error = '無法載入行事曆資料';
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

    // Format dates properly for API
    const scheduleData: ScheduleCreateDto = {
      title: formData.title,
      description: formData.description,
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
      
      this.scheduleForm.patchValue({
        title: schedule.title,
        description: schedule.description,
        start_time: this.formatDateForInput(startTime),
        end_time: endTime ? this.formatDateForInput(endTime) : ''
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
    }
  }

  // Helper to format date for datetime-local input
  private formatDateForInput(date: Date): string {
    return date.toISOString().slice(0, 16);
  }
}
