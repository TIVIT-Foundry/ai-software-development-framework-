/**
 * React Page Component Template
 *
 * Page = componente de nivel superior asociado a una ruta lazy-loaded.
 * Diferencia de un componente normal:
 * - Es el entry point de una ruta (React.lazy / Next.js route segment)
 * - Orquesta datos: consume hooks de react-services (TanStack Query) y stores Zustand
 * - Suele ser más grande que un componente de presentación
 * - Setea el título de página (document.title o Next.js metadata)
 *
 * Convenciones:
 * - Function component, sin clases
 * - Estado de página con useState/useReducer
 * - Datos vía hooks de react-services (useQuery/useMutation)
 * - Título de página con useEffect (Vite) o export const metadata (Next.js)
 *
 * Uso: Copiar este archivo, renombrar el componente y el archivo,
 *       reemplazar los placeholders.
 */

import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

// --- Importa tus propios hooks, stores y componentes ---
// import { use{{ModelName}}s, useDelete{{ModelName}} } from '../hooks/use{{ModelName}}s';
// import { use{{ModelName}}Store } from '../stores/{{model-name}}.store';
// import type { {{ModelName}} } from '../models/{{model-name}}.types';

export function {{ComponentName}}Page() {
  const navigate = useNavigate();
  const params = useParams();

  // --- Datos vía hooks de react-services (equivalente a inject(Service) + toSignal) ---
  // const { data: items, isLoading, isError, error } = use{{ModelName}}s();
  // const deleteMutation = useDelete{{ModelName}}();

  // --- Estado de UI ---
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFilter, setSelectedFilter] = useState<string>('all');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  // --- Título de página ---
  useEffect(() => {
    document.title = '{{PageTitle}} | App';
  }, []);

  // --- Datos filtrados / ordenados localmente ---
  // const filteredItems = useMemo(() => {
  //   const term = searchTerm.toLowerCase();
  //   let result = items ?? [];
  //   if (term) result = result.filter((item) => item.name.toLowerCase().includes(term));
  //   if (selectedFilter !== 'all') result = result.filter((item) => item.status === selectedFilter);
  //   return [...result].sort((a, b) => (sortDirection === 'asc' ? 1 : -1) * a.name.localeCompare(b.name));
  // }, [items, searchTerm, selectedFilter, sortDirection]);

  // --- Handlers de usuario ---
  const handleSearch = (term: string) => setSearchTerm(term);
  const handleFilterChange = (filter: string) => setSelectedFilter(filter);
  const handleSortToggle = () => setSortDirection((d) => (d === 'asc' ? 'desc' : 'asc'));

  // const handleSelectItem = (item: {{ModelName}}) => navigate(`${item.id}`);
  // const handleCreateItem = () => navigate('new');
  // const handleDeleteItem = (id: string) => deleteMutation.mutate(id);

  return (
    <section>
      <header>
        <h1>{{PageTitle}}</h1>
        <input value={searchTerm} onChange={(e) => handleSearch(e.target.value)} placeholder="Search..." />
        <button onClick={handleSortToggle}>Sort ({sortDirection})</button>
      </header>

      {/* {isLoading && <div className="spinner">Loading...</div>} */}
      {/* {isError && <div className="error">{error?.message}</div>} */}
      {/* {!isLoading && !isError && filteredItems.length === 0 && <div className="empty">No items</div>} */}
    </section>
  );
}
