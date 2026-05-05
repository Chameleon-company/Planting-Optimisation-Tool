import type {
  FormState,
  FormErrors,
} from "@/components/farmManagement/farmForms/farmConstantsForm";

type BooleanFlag =
  | "coastal"
  | "nitrogen_fixing"
  | "shade_tolerant"
  | "bank_stabilising";

const BOOLEAN_FLAGS: { name: BooleanFlag; label: string }[] = [
  { name: "coastal", label: "Coastal" },
  { name: "nitrogen_fixing", label: "Nitrogen fixing" },
  { name: "shade_tolerant", label: "Shade tolerant" },
  { name: "bank_stabilising", label: "Bank stabilising" },
];

interface SoilTexture {
  id: number;
  name: string;
}

interface AgroforestryType {
  id: number;
  name: string;
}

interface FarmFormFieldsProps {
  form: FormState;
  errors: FormErrors;
  isSubmitting: boolean;
  onChange: (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => void;
  onAgroforestryToggle: (id: number) => void;
  onBooleanToggle: (name: BooleanFlag) => void;
  soilTextures: SoilTexture[];
  agroforestryTypes: AgroforestryType[];
}

export default function FarmFormFields({
  form,
  errors,
  isSubmitting,
  onChange,
  onAgroforestryToggle,
  onBooleanToggle,
  soilTextures,
  agroforestryTypes,
}: FarmFormFieldsProps) {
  return (
    <div className="register-farm-grid">
      {/*  Number fields */}
      <div className="register-farm-field">
        <label className="register-farm-label" htmlFor="rainfall_mm">
          Rainfall (mm) <span className="register-farm-required">*</span>
        </label>
        <input
          id="rainfall_mm"
          name="rainfall_mm"
          type="number"
          min="0"
          className={`register-farm-input ${errors.rainfall_mm ? "register-farm-input-error" : ""}`}
          value={form.rainfall_mm}
          onChange={onChange}
          disabled={isSubmitting}
        />
        {errors.rainfall_mm && (
          <span className="register-farm-error">{errors.rainfall_mm}</span>
        )}
      </div>

      <div className="register-farm-field">
        <label className="register-farm-label" htmlFor="temperature_celsius">
          Temperature (°C) <span className="register-farm-required">*</span>
        </label>
        <input
          id="temperature_celsius"
          name="temperature_celsius"
          type="number"
          className={`register-farm-input ${errors.temperature_celsius ? "register-farm-input-error" : ""}`}
          value={form.temperature_celsius}
          onChange={onChange}
          disabled={isSubmitting}
        />
        {errors.temperature_celsius && (
          <span className="register-farm-error">
            {errors.temperature_celsius}
          </span>
        )}
      </div>

      <div className="register-farm-field">
        <label className="register-farm-label" htmlFor="elevation_m">
          Elevation (m) <span className="register-farm-required">*</span>
        </label>
        <input
          id="elevation_m"
          name="elevation_m"
          type="number"
          className={`register-farm-input ${errors.elevation_m ? "register-farm-input-error" : ""}`}
          value={form.elevation_m}
          onChange={onChange}
          disabled={isSubmitting}
        />
        {errors.elevation_m && (
          <span className="register-farm-error">{errors.elevation_m}</span>
        )}
      </div>

      <div className="register-farm-field">
        <label className="register-farm-label" htmlFor="ph">
          Soil pH <span className="register-farm-required">*</span>
        </label>
        <input
          id="ph"
          name="ph"
          type="number"
          min="0"
          max="14"
          step="0.1"
          className={`register-farm-input ${errors.ph ? "register-farm-input-error" : ""}`}
          value={form.ph}
          onChange={onChange}
          disabled={isSubmitting}
        />
        {errors.ph && <span className="register-farm-error">{errors.ph}</span>}
      </div>

      <div className="register-farm-field">
        <label className="register-farm-label" htmlFor="area_ha">
          Area (ha) <span className="register-farm-required">*</span>
        </label>
        <input
          id="area_ha"
          name="area_ha"
          type="number"
          min="0"
          step="0.001"
          className={`register-farm-input ${errors.area_ha ? "register-farm-input-error" : ""}`}
          value={form.area_ha}
          onChange={onChange}
          disabled={isSubmitting}
        />
        {errors.area_ha && (
          <span className="register-farm-error">{errors.area_ha}</span>
        )}
      </div>

      <div className="register-farm-field">
        <label className="register-farm-label" htmlFor="slope">
          Slope (°) <span className="register-farm-required">*</span>
        </label>
        <input
          id="slope"
          name="slope"
          type="number"
          min="0"
          step="0.01"
          className={`register-farm-input ${errors.slope ? "register-farm-input-error" : ""}`}
          value={form.slope}
          onChange={onChange}
          disabled={isSubmitting}
        />
        {errors.slope && (
          <span className="register-farm-error">{errors.slope}</span>
        )}
      </div>

      <div className="register-farm-field">
        <label className="register-farm-label" htmlFor="latitude">
          Latitude <span className="register-farm-required">*</span>
        </label>
        <input
          id="latitude"
          name="latitude"
          type="number"
          min="-90"
          max="90"
          step="0.00001"
          className={`register-farm-input ${errors.latitude ? "register-farm-input-error" : ""}`}
          value={form.latitude}
          onChange={onChange}
          disabled={isSubmitting}
        />
        {errors.latitude && (
          <span className="register-farm-error">{errors.latitude}</span>
        )}
      </div>

      <div className="register-farm-field">
        <label className="register-farm-label" htmlFor="longitude">
          Longitude <span className="register-farm-required">*</span>
        </label>
        <input
          id="longitude"
          name="longitude"
          type="number"
          min="-180"
          max="180"
          step="0.00001"
          className={`register-farm-input ${errors.longitude ? "register-farm-input-error" : ""}`}
          value={form.longitude}
          onChange={onChange}
          disabled={isSubmitting}
        />
        {errors.longitude && (
          <span className="register-farm-error">{errors.longitude}</span>
        )}
      </div>

      {/* Soil texture dropdown */}
      <div className="register-farm-field register-farm-field-full">
        <label className="register-farm-label" htmlFor="soil_texture_id">
          Soil texture <span className="register-farm-required">*</span>
        </label>
        <select
          id="soil_texture_id"
          name="soil_texture_id"
          className={`register-farm-input ${errors.soil_texture_id ? "register-farm-input-error" : ""}`}
          value={form.soil_texture_id}
          onChange={onChange}
          disabled={isSubmitting}
        >
          <option value="">Select soil texture…</option>
          {soilTextures.map(opt => (
            <option key={opt.id} value={opt.id}>
              {opt.name}
            </option>
          ))}
        </select>
        {errors.soil_texture_id && (
          <span className="register-farm-error">{errors.soil_texture_id}</span>
        )}
      </div>

      {/* Agroforestry types (multi-select toggle) */}
      <div className="register-farm-field register-farm-field-full">
        <label className="register-farm-label">
          Agroforestry type <span className="register-farm-required">*</span>
        </label>
        <div className="register-farm-toggle-group">
          {agroforestryTypes.map(opt => (
            <button
              key={opt.id}
              type="button"
              className={`register-farm-toggle ${form.agroforestry_type_ids.includes(opt.id) ? "register-farm-toggle-active" : ""}`}
              onClick={() => onAgroforestryToggle(opt.id)}
              disabled={isSubmitting}
            >
              {opt.name}
            </button>
          ))}
        </div>
        {errors.agroforestry_type_ids && (
          <span className="register-farm-error">
            {errors.agroforestry_type_ids}
          </span>
        )}
      </div>

      {/* Boolean flags  */}
      <div className="register-farm-field register-farm-field-full">
        <label className="register-farm-label">Characteristics</label>
        <div className="register-farm-toggle-group">
          {BOOLEAN_FLAGS.map(({ name, label }) => (
            <button
              key={name}
              type="button"
              className={`register-farm-toggle ${form[name] ? "register-farm-toggle-active" : ""}`}
              onClick={() => onBooleanToggle(name)}
              disabled={isSubmitting}
            >
              {label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
