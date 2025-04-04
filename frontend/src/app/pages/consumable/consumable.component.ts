import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Consumable, ConsumableCreateDto } from '../../shared/models/consumable.model';
import { ConsumableService } from '../../shared/services/consumable.service';

@Component({
  selector: 'app-consumable',
  templateUrl: './consumable.component.html',
  styleUrls: ['./consumable.component.scss']
})
export class ConsumableComponent implements OnInit {
  consumables: Consumable[] = [];
  consumableForm: FormGroup;
  isLoading = true;
  isSubmitting = false;
  editingConsumableId: number | null = null;
  showForm = false;
  error: string | null = null;
  
  // 耗材分類選項
  categories = [
    '濾水器',
    '空氣清淨機濾網',
    '冷氣濾網',
    '吸塵器濾網',
    '其他'
  ];

  constructor(
    private consumableService: ConsumableService,
    private fb: FormBuilder
  ) {
    this.consumableForm = this.fb.group({
      name: ['', [Validators.required]],
      category: ['', [Validators.required]],
      installation_date: ['', [Validators.required]],
      lifetime_days: [90, [Validators.required, Validators.min(1)]],
      notes: ['']
    });
  }

  ngOnInit(): void {
    this.loadConsumables();
  }

  loadConsumables(): void {
    this.isLoading = true;
    this.consumableService.getConsumables().subscribe({
      next: (data) => {
        this.consumables = data;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading consumables', error);
        this.error = '無法載入耗材資料';
        this.isLoading = false;
      }
    });
  }

  onSubmit(): void {
    if (this.consumableForm.invalid) {
      return;
    }

    this.isSubmitting = true;
    const formData = this.consumableForm.value;

    // Format dates properly for API
    const consumableData: ConsumableCreateDto = {
      name: formData.name,
      category: formData.category,
      installation_date: formData.installation_date,
      lifetime_days: formData.lifetime_days,
      notes: formData.notes
    };

    if (this.editingConsumableId) {
      this.consumableService.updateConsumable(this.editingConsumableId, consumableData).subscribe({
        next: () => {
          this.resetForm();
          this.loadConsumables();
        },
        error: (error) => {
          console.error('Error updating consumable', error);
          this.error = '更新耗材失敗';
          this.isSubmitting = false;
        }
      });
    } else {
      this.consumableService.createConsumable(consumableData).subscribe({
        next: () => {
          this.resetForm();
          this.loadConsumables();
        },
        error: (error) => {
          console.error('Error creating consumable', error);
          this.error = '新增耗材失敗';
          this.isSubmitting = false;
        }
      });
    }
  }

  editConsumable(consumable: Consumable): void {
    if (consumable.id) {
      this.editingConsumableId = consumable.id;
      this.showForm = true;
      
      this.consumableForm.patchValue({
        name: consumable.name,
        category: consumable.category,
        installation_date: this.formatDateForInput(new Date(consumable.installation_date)),
        lifetime_days: consumable.lifetime_days,
        notes: consumable.notes
      });
    }
  }

  deleteConsumable(id: number): void {
    if (confirm('確定要刪除此耗材記錄嗎?')) {
      this.consumableService.deleteConsumable(id).subscribe({
        next: () => {
          this.loadConsumables();
        },
        error: (error) => {
          console.error('Error deleting consumable', error);
          this.error = '刪除耗材失敗';
        }
      });
    }
  }

  resetForm(): void {
    this.consumableForm.reset({
      category: '',
      lifetime_days: 90
    });
    this.editingConsumableId = null;
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

  getStatusClass(daysRemaining?: number): string {
    if (daysRemaining === undefined) return '';
    if (daysRemaining <= 0) return 'badge-danger';
    if (daysRemaining < 30) return 'badge-warning';
    return 'badge-success';
  }

  // Helper to format date for date input (YYYY-MM-DD)
  private formatDateForInput(date: Date): string {
    return date.toISOString().split('T')[0];
  }
}
