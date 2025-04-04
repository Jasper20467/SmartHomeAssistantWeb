export interface Schedule {
  id?: number;
  title: string;
  description?: string;
  start_time: Date | string;
  end_time?: Date | string;
  created_at?: Date | string;
  updated_at?: Date | string;
}

export interface ScheduleCreateDto {
  title: string;
  description?: string;
  start_time: string;
  end_time?: string;
}

export interface ScheduleUpdateDto {
  title?: string;
  description?: string;
  start_time?: string;
  end_time?: string;
}
