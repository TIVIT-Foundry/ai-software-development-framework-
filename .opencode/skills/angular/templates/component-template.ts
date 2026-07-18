/**
 * Angular Standalone Component Template
 *
 * Convenciones aplicadas:
 * - standalone: true
 * - ChangeDetectionStrategy.OnPush
 * - Estado local con signals (signal, computed)
 * - DI con inject()
 * - Inputs tipados con input.required<T>() / input<T>()
 * - Outputs tipados con output<T>()
 * - Template inline o templateUrl
 * - Estilos scoped con styleUrl o styles
 *
 * Uso: Copiar este archivo, renombrar la clase y selector,
 *       reemplazar los placeholders ({{ClassName}}, {{selector}}, etc.)
 */

import {
  Component,
  signal,
  computed,
  input,
  output,
  effect,
  ChangeDetectionStrategy,
  OnInit,
  OnDestroy,
  inject,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

// --- Modelos de ejemplo (reemplazar con los reales) ---
interface {{ModelName}} {
  id: string;
  name: string;
  status: 'active' | 'inactive' | 'pending';
  createdAt: Date;
}

// --- Componente ---
@Component({
  selector: 'app-{{selector}}',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './{{file-name}}.component.html',
  styleUrl: './{{file-name}}.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class {{ClassName}}Component implements OnInit, OnDestroy {
  // --- Inputs (propiedades recibidas del padre) ---
  readonly item = input.required<{{ModelName}}>();
  readonly disabled = input(false);
  readonly variant = input<'default' | 'compact' | 'expanded'>('default');

  // --- Outputs (eventos emitidos al padre) ---
  readonly selected = output<{{ModelName}}>();
  readonly deleted = output<string>();
  readonly toggled = output<boolean>();

  // --- Estado local con signals ---
  private isExpanded = signal(false);
  private isHovered = signal(false);

  // --- Dependencias inyectadas ---
  // private someService = inject(SomeService);

  // --- Computed signals (derivadas del estado) ---
  readonly statusClass = computed(() => {
    const status = this.item().status;
    const classes: Record<string, string> = {
      active: 'status-active',
      inactive: 'status-inactive',
      pending: 'status-pending',
    };
    return classes[status] ?? 'status-unknown';
  });

  readonly cssClasses = computed(() => ({
    [this.statusClass()]: true,
    'is-expanded': this.isExpanded(),
    'is-hovered': this.isHovered(),
    'is-disabled': this.disabled(),
    [`variant-${this.variant()}`]: true,
  }));

  readonly displayName = computed(() => {
    const item = this.item();
    return item.name?.trim() || '(sin nombre)';
  });

  // --- Effect para side effects reactivos ---
  private _logEffect = effect(() => {
    // Se ejecuta cada vez que item() cambia
    const item = this.item();
    console.debug(`[{{ClassName}}] Item cargado: ${item.id}`);
  });

  // --- Lifecycle hooks ---
  ngOnInit(): void {
    // Inicialización que no depende del template
  }

  ngOnDestroy(): void {
    // Limpieza de recursos (aunque effects se limpian automáticamente)
  }

  // --- Métodos públicos (handlers del template) ---
  onSelect(): void {
    if (this.disabled()) return;
    this.selected.emit(this.item());
  }

  onToggle(): void {
    this.isExpanded.update(v => !v);
    this.toggled.emit(this.isExpanded());
  }

  onDelete(): void {
    this.deleted.emit(this.item().id);
  }

  onMouseEnter(): void {
    this.isHovered.set(true);
  }

  onMouseLeave(): void {
    this.isHovered.set(false);
  }

  // --- Métodos privados ---
  private logEvent(event: string): void {
    console.debug(`[{{ClassName}}] Evento: ${event}`, {
      itemId: this.item().id,
      timestamp: new Date().toISOString(),
    });
  }
}
