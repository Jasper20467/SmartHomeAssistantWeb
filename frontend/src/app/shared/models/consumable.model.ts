export interface Consumable {
  id?: number;
  name: string;
  category: string;
  installation_date: Date | string;
  lifetime_days: number;
  notes?: string;
  created_at?: Date | string;
  updated_at?: Date | string;
  days_remaining?: number;
}

export interface ConsumableCreateDto {
  name: string;
  category: string;
  installation_date: string;
  lifetime_days: number;
  notes?: string;
}

export interface ConsumableUpdateDto {
  name?: string;
  category?: string;
  installation_date?: string;
  lifetime_days?: number;
  notes?: string;
}
