/**
 * Angular Page Component Template
 *
 * Page = componente de nivel superior asociado a una ruta lazy-loaded.
 * Diferencia de un componente normal:
 * - Es el entry point de una ruta (loadComponent)
 * - Orquesta datos: inyecta servicios y stores
 * - Suele ser más grande que un componente de presentación
 * - Puede tener título de página y meta tags
 *
 * Convenciones:
 * - standalone: true, OnPush
 * - Estado local con signals + store signals
 * - Datos vía servicios inyectados con inject()
 * - toSignal() para convertir Observables a signals
 * - Template externo con control flow (@if, @for, @switch)
 *
 * Uso: Copiar este archivo, renombrar clase y selector,
 *       reemplazar los placeholders.
 */

import {
  Component,
  signal,
  computed,
  inject,
  OnInit,
  ChangeDetectionStrategy,
  DestroyRef,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { CommonModule } from '@angular/common';
import { RouterLink, ActivatedRoute, Router } from '@angular/router';
import { Title } from '@angular/platform-browser';
import { toSignal } from '@angular/core/rxjs-interop';

// --- Importa tus propios servicios, stores y componentes ---
// import { {{ModelName}}Service } from '../../core/services/{{model-name}}.service';
// import { {{ModelName}}Store } from '../../core/stores/{{model-name}}.store';
// import { {{ModelName}} } from '../../core/models/{{model-name}}.types';

// --- Estados de carga tipados ---
type PageState = {
  loading: boolean;
  error: string | null;
  saving: boolean;
};

@Component({
  selector: 'app-{{selector}}-page',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './{{file-name}}-page.component.html',
  styleUrl: './{{file-name}}-page.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class {{ClassName}}PageComponent implements OnInit {
  // --- Dependencias inyectadas ---
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private titleService = inject(Title);
  private destroyRef = inject(DestroyRef);

  // --- Servicios y stores propios ---
  // private service = inject({{ModelName}}Service);
  // private store = inject({{ModelName}}Store);

  // --- Estado de página ---
  private pageState = signal<PageState>({
    loading: false,
    error: null,
    saving: false,
  });

  // --- Estado de UI ---
  private searchTerm = signal('');
  private selectedFilter = signal<string>('all');
  private sortDirection = signal<'asc' | 'desc'>('asc');

  // --- Datos derivados ---
  readonly isLoading = computed(() => this.pageState().loading);
  readonly hasError = computed(() => this.pageState().error !== null);
  readonly errorMessage = computed(() => this.pageState().error);
  readonly isSaving = computed(() => this.pageState().saving);

  // --- Signals del store (expuestos como readonly) ---
  // readonly items = this.store.itemList;
  // readonly totalCount = this.store.totalCount;

  // --- Datos filtrados / ordenados localmente ---
  // readonly filteredItems = computed(() => {
  //   const term = this.searchTerm().toLowerCase();
  //   const filter = this.selectedFilter();
  //   const items = this.items();
  //
  //   let result = items;
  //   if (term) {
  //     result = result.filter(item => item.name.toLowerCase().includes(term));
  //   }
  //   if (filter !== 'all') {
  //     result = result.filter(item => item.status === filter);
  //   }
  //
  //   return result.sort((a, b) => {
  //     const dir = this.sortDirection() === 'asc' ? 1 : -1;
  //     return dir * a.name.localeCompare(b.name);
  //   });
  // });

  // --- Lifecycle ---
  ngOnInit(): void {
    this.titleService.setTitle('{{PageTitle}} | App');
    this.loadData();
  }

  // --- Carga de datos ---
  loadData(): void {
    this.pageState.update(s => ({ ...s, loading: true, error: null }));

    // Patrón con servicio que devuelve Observable:
    // this.service.getItems()
    //   .pipe(takeUntilDestroyed(this.destroyRef))
    //   .subscribe({
    //     next: (items) => {
    //       this.store.setItems(items);
    //       this.pageState.update(s => ({ ...s, loading: false }));
    //     },
    //     error: (err) => {
    //       this.pageState.update(s => ({
    //         ...s,
    //         loading: false,
    //         error: err?.message ?? 'Error al cargar datos',
    //       }));
    //     },
    //   });

    // Patrón con toSignal (preferido):
    // const items$ = this.service.getItems();
    // const itemsSignal = toSignal(items$, { initialValue: [] });
    // este signal se puede usar directamente en el template
  }

  // --- Handlers de usuario ---
  onSearch(term: string): void {
    this.searchTerm.set(term);
  }

  onFilterChange(filter: string): void {
    this.selectedFilter.set(filter);
  }

  onSortToggle(): void {
    this.sortDirection.update(d => d === 'asc' ? 'desc' : 'asc');
  }

  onRefresh(): void {
    this.loadData();
  }

  onRetry(): void {
    this.loadData();
  }

  // onSelectItem(item: {{ModelName}}): void {
  //   this.router.navigate([item.id], { relativeTo: this.route });
  // }

  // onCreateItem(): void {
  //   this.router.navigate(['new'], { relativeTo: this.route });
  // }

  // onDeleteItem(id: string): void {
  //   this.pageState.update(s => ({ ...s, saving: true }));
  //
  //   this.service.deleteItem(id)
  //     .pipe(takeUntilDestroyed(this.destroyRef))
  //     .subscribe({
  //       next: () => {
  //         this.store.removeItem(id);
  //         this.pageState.update(s => ({ ...s, saving: false }));
  //       },
  //       error: (err) => {
  //         this.pageState.update(s => ({
  //           ...s,
  //           saving: false,
  //           error: err?.message ?? 'Error al eliminar',
  //         }));
  //       },
  //     });
  // }
}
