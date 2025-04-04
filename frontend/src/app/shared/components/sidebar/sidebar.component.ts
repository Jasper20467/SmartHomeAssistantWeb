import { Component } from '@angular/core';

interface SidebarItem {
  name: string;
  route: string;
  icon: string;
}

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.scss']
})
export class SidebarComponent {
  menuItems: SidebarItem[] = [
    {
      name: '儀表板',
      route: '/dashboard',
      icon: '📊'
    },
    {
      name: '行事曆',
      route: '/schedule',
      icon: '📅'
    },
    {
      name: '耗材管理',
      route: '/consumable',
      icon: '🔧'
    }
  ];
}
