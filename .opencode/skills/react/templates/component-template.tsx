/**
 * React Function Component Template
 *
 * Convenciones aplicadas:
 * - Function component tipado (sin clases)
 * - Estado local con useState
 * - Valores derivados con useMemo
 * - Efectos con useEffect (con cleanup)
 * - Props tipadas con interface
 * - Callbacks memoizados con useCallback cuando se pasan a hijos memoizados
 *
 * Uso: Copiar este archivo, renombrar el componente y el archivo,
 *       reemplazar los placeholders ({{ComponentName}}, {{ModelName}}, etc.)
 */

import { useCallback, useEffect, useMemo, useState } from 'react';

// --- Modelos de ejemplo (reemplazar con los reales) ---
interface {{ModelName}} {
  id: string;
  name: string;
  status: 'active' | 'inactive' | 'pending';
  createdAt: string;
}

// --- Props ---
interface {{ComponentName}}Props {
  item: {{ModelName}};
  disabled?: boolean;
  variant?: 'default' | 'compact' | 'expanded';
  onSelect: (item: {{ModelName}}) => void;
  onDelete: (id: string) => void;
  onToggle?: (expanded: boolean) => void;
}

// --- Componente ---
export function {{ComponentName}}({
  item,
  disabled = false,
  variant = 'default',
  onSelect,
  onDelete,
  onToggle,
}: {{ComponentName}}Props) {
  // --- Estado local ---
  const [isExpanded, setIsExpanded] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  // --- Valores derivados (computed) ---
  const statusClass = useMemo(() => {
    const classes: Record<string, string> = {
      active: 'status-active',
      inactive: 'status-inactive',
      pending: 'status-pending',
    };
    return classes[item.status] ?? 'status-unknown';
  }, [item.status]);

  const cssClasses = useMemo(
    () =>
      [
        statusClass,
        isExpanded && 'is-expanded',
        isHovered && 'is-hovered',
        disabled && 'is-disabled',
        `variant-${variant}`,
      ]
        .filter(Boolean)
        .join(' '),
    [statusClass, isExpanded, isHovered, disabled, variant]
  );

  const displayName = useMemo(() => item.name?.trim() || '(sin nombre)', [item.name]);

  // --- Efecto de logging (equivalente a un signal effect) ---
  useEffect(() => {
    console.debug(`[{{ComponentName}}] Item cargado: ${item.id}`);
  }, [item.id]);

  // --- Handlers memoizados ---
  const handleSelect = useCallback(() => {
    if (disabled) return;
    onSelect(item);
  }, [disabled, onSelect, item]);

  const handleToggle = useCallback(() => {
    setIsExpanded((prev) => {
      const next = !prev;
      onToggle?.(next);
      return next;
    });
  }, [onToggle]);

  const handleDelete = useCallback(() => {
    onDelete(item.id);
  }, [onDelete, item.id]);

  return (
    <div
      className={cssClasses}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <h3>{displayName}</h3>
      <button onClick={handleSelect} disabled={disabled}>Select</button>
      <button onClick={handleToggle}>{isExpanded ? 'Collapse' : 'Expand'}</button>
      <button onClick={handleDelete}>Delete</button>
    </div>
  );
}
