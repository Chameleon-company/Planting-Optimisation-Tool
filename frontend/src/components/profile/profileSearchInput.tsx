interface FarmSearchInputProps {
  value: string;
  onChange: (value: string) => void;
  onClear: () => void;
  isLoading: boolean;
}

export default function FarmSearchInput({
  value,
  onChange,
  onClear,
  isLoading,
}: FarmSearchInputProps) {
  return (
    <div className="profile-search">
      <input
        value={value}
        onChange={e => onChange(e.target.value)}
        disabled={isLoading}
        className="search-input"
        placeholder="Search by farm ID..."
      />

      {value && (
        <button onClick={onClear} className="btn-primary">
          Clear
        </button>
      )}
    </div>
  );
}
