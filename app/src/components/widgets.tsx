// Widgets de control reutilizables.

interface RangeProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  unit?: string;
  fmt?: (v: number) => string;
  onChange: (v: number) => void;
}

export function RangeField({
  label,
  value,
  min,
  max,
  step = 1,
  unit = "",
  fmt,
  onChange,
}: RangeProps) {
  const shown = fmt ? fmt(value) : `${value}${unit ? " " + unit : ""}`;
  return (
    <div className="field">
      <label>
        {label}: <span className="value">{shown}</span>
      </label>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
      />
    </div>
  );
}

interface SelectProps<T extends string> {
  label: string;
  value: T;
  options: { value: T; label: string }[];
  onChange: (v: T) => void;
}

export function SelectField<T extends string>({
  label,
  value,
  options,
  onChange,
}: SelectProps<T>) {
  return (
    <div className="field">
      <label>{label}</label>
      <select value={value} onChange={(e) => onChange(e.target.value as T)}>
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </div>
  );
}

interface ChipGroupProps<T extends string> {
  value: T;
  options: { value: T; label: string; className?: string }[];
  onChange: (v: T) => void;
}

export function ChipGroup<T extends string>({
  value,
  options,
  onChange,
}: ChipGroupProps<T>) {
  return (
    <div className="chips">
      {options.map((o) => (
        <button
          key={o.value}
          className={`chip ${o.className ?? ""} ${o.value === value ? "active" : ""}`}
          onClick={() => onChange(o.value)}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}
