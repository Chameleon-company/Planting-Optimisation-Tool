import {
  SOIL_TEXTURE_OPTIONS,
  AGROFORESTRY_TYPE_OPTIONS,
} from "@/components/farmManagement/farmForms/farmConstantsForm";
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

interface FarmFormFieldsProps {
  form: FormState;
  errors: FormErrors;
  isSubmitting: boolean;
  onChange: (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => void;
  onAgroforestryToggle: (id: number) => void;
  onBooleanToggle: (name: BooleanFlag) => void;
}

export default function FarmFormFields({
  form,
  errors,
  isSubmitting,
  onChange,
  onAgroforestryToggle,
  onBooleanToggle,
}: FarmFormFieldsProps) {
  return (
    <div className="registerFarmGrid">
      {/*  Number fields */}
      <div className="registerFarmField">
        <label className="registerFarmLabel" htmlFor="rainfall_mm">
          Rainfall (mm) <span className="registerFarmRequired">*</span>
        </label>
        <input
          id="rainfall_mm"
          name="rainfall_mm"
          type="number"
          min="0"
          className={`registerFarmInput ${errors.rainfall_mm ? "registerFarmInputError" : ""}`}
          value={form.rainfall_mm}
          onChange={onChange}
          disabled={isSubmitting}
        />
        {errors.rainfall_mm && (
          <span className="registerFarmError">{errors.rainfall_mm}</span>
        )}
      </div>

      <div className="registerFarmField">
        <label className="registerFarmLabel" htmlFor="temperature_celsius">
          Temperature (°C) <span className="registerFarmRequired">*</span>
        </label>
        <input
          id="temperature_celsius"
          name="temperature_celsius"
          type="number"
          className={`registerFarmInput ${errors.temperature_celsius ? "registerFarmInputError" : ""}`}
          value={form.temperature_celsius}
          onChange={onChange}
          disabled={isSubmitting}
        />
        {errors.temperature_celsius && (
          <span className="registerFarmError">
            {errors.temperature_celsius}
          </span>
        )}
      </div>

      <div className="registerFarmField">
        <label className="registerFarmLabel" htmlFor="elevation_m">
          Elevation (m) <span className="registerFarmRequired">*</span>
        </label>
        <input
          id="elevation_m"
          name="elevation_m"
          type="number"
          className={`registerFarmInput ${errors.elevation_m ? "registerFarmInputError" : ""}`}
          value={form.elevation_m}
          onChange={onChange}
          disabled={isSubmitting}
        />
        {errors.elevation_m && (
          <span className="registerFarmError">{errors.elevation_m}</span>
        )}
      </div>

      <div className="registerFarmField">
        <label className="registerFarmLabel" htmlFor="ph">
          Soil pH <span className="registerFarmRequired">*</span>
        </label>
        <input
          id="ph"
          name="ph"
          type="number"
          min="0"
          max="14"
          step="0.1"
          className={`registerFarmInput ${errors.ph ? "registerFarmInputError" : ""}`}
          value={form.ph}
          onChange={onChange}
          disabled={isSubmitting}
        />
        {errors.ph && <span className="registerFarmError">{errors.ph}</span>}
      </div>

      <div className="registerFarmField">
        <label className="registerFarmLabel" htmlFor="area_ha">
          Area (ha) <span className="registerFarmRequired">*</span>
        </label>
        <input
          id="area_ha"
          name="area_ha"
          type="number"
          min="0"
          step="0.001"
          className={`registerFarmInput ${errors.area_ha ? "registerFarmInputError" : ""}`}
          value={form.area_ha}
          onChange={onChange}
          disabled={isSubmitting}
        />
        {errors.area_ha && (
          <span className="registerFarmError">{errors.area_ha}</span>
        )}
      </div>

      <div className="registerFarmField">
        <label className="registerFarmLabel" htmlFor="slope">
          Slope (°) <span className="registerFarmRequired">*</span>
        </label>
        <input
          id="slope"
          name="slope"
          type="number"
          min="0"
          step="0.01"
          className={`registerFarmInput ${errors.slope ? "registerFarmInputError" : ""}`}
          value={form.slope}
          onChange={onChange}
          disabled={isSubmitting}
        />
        {errors.slope && (
          <span className="registerFarmError">{errors.slope}</span>
        )}
      </div>

      <div className="registerFarmField">
        <label className="registerFarmLabel" htmlFor="latitude">
          Latitude <span className="registerFarmRequired">*</span>
        </label>
        <input
          id="latitude"
          name="latitude"
          type="number"
          min="-90"
          max="90"
          step="0.00001"
          className={`registerFarmInput ${errors.latitude ? "registerFarmInputError" : ""}`}
          value={form.latitude}
          onChange={onChange}
          disabled={isSubmitting}
        />
        {errors.latitude && (
          <span className="registerFarmError">{errors.latitude}</span>
        )}
      </div>

      <div className="registerFarmField">
        <label className="registerFarmLabel" htmlFor="longitude">
          Longitude <span className="registerFarmRequired">*</span>
        </label>
        <input
          id="longitude"
          name="longitude"
          type="number"
          min="-180"
          max="180"
          step="0.00001"
          className={`registerFarmInput ${errors.longitude ? "registerFarmInputError" : ""}`}
          value={form.longitude}
          onChange={onChange}
          disabled={isSubmitting}
        />
        {errors.longitude && (
          <span className="registerFarmError">{errors.longitude}</span>
        )}
      </div>

      {/* Soil texture dropdown */}
      <div className="registerFarmField registerFarmFieldFull">
        <label className="registerFarmLabel" htmlFor="soil_texture_id">
          Soil texture <span className="registerFarmRequired">*</span>
        </label>
        <select
          id="soil_texture_id"
          name="soil_texture_id"
          className={`registerFarmInput ${errors.soil_texture_id ? "registerFarmInputError" : ""}`}
          value={form.soil_texture_id}
          onChange={onChange}
          disabled={isSubmitting}
        >
          <option value="">Select soil texture…</option>
          {SOIL_TEXTURE_OPTIONS.map(opt => (
            <option key={opt.id} value={opt.id}>
              {opt.label}
            </option>
          ))}
        </select>
        {errors.soil_texture_id && (
          <span className="registerFarmError">{errors.soil_texture_id}</span>
        )}
      </div>

      {/* Agroforestry types (multi-select toggle) */}
      <div className="registerFarmField registerFarmFieldFull">
        <label className="registerFarmLabel">
          Agroforestry type <span className="registerFarmRequired">*</span>
        </label>
        <div className="registerFarmToggleGroup">
          {AGROFORESTRY_TYPE_OPTIONS.map(opt => (
            <button
              key={opt.id}
              type="button"
              className={`registerFarmToggle ${form.agroforestry_type_ids.includes(opt.id) ? "registerFarmToggleActive" : ""}`}
              onClick={() => onAgroforestryToggle(opt.id)}
              disabled={isSubmitting}
            >
              {opt.label}
            </button>
          ))}
        </div>
        {errors.agroforestry_type_ids && (
          <span className="registerFarmError">
            {errors.agroforestry_type_ids}
          </span>
        )}
      </div>

      {/* Boolean flags  */}
      <div className="registerFarmField registerFarmFieldFull">
        <label className="registerFarmLabel">Characteristics</label>
        <div className="registerFarmToggleGroup">
          {BOOLEAN_FLAGS.map(({ name, label }) => (
            <button
              key={name}
              type="button"
              className={`registerFarmToggle ${form[name] ? "registerFarmToggleActive" : ""}`}
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
