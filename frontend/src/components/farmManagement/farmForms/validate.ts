import type {
  FormState,
  FormErrors,
} from "@/components/farmManagement/farmForms/farmConstantsForm";

export function validate(
  form: FormState,
  mode: "register" | "edit"
): FormErrors {
  const errors: FormErrors = {};

  // Rainfall, must be ge than 500, less than 3000
  if (!form.rainfall_mm.trim()) {
    errors.rainfall_mm = "Rainfall is required.";
  } else if (
    isNaN(Number(form.rainfall_mm)) ||
    !Number.isInteger(Number(form.rainfall_mm))
  ) {
    errors.rainfall_mm = "Must be a whole number.";
  } else if (
    Number(form.rainfall_mm) < 500 ||
    Number(form.rainfall_mm) > 3000
  ) {
    errors.rainfall_mm = "Must be between 500 and 3000 mm.";
  }

  // Temperature, greater than 15, less than 30 (integer)
  if (!form.temperature_celsius.trim()) {
    errors.temperature_celsius = "Temperature is required.";
  } else if (
    isNaN(Number(form.temperature_celsius)) ||
    !Number.isInteger(Number(form.temperature_celsius))
  ) {
    errors.temperature_celsius = "Must be a whole number.";
  } else if (
    Number(form.temperature_celsius) < 15 ||
    Number(form.temperature_celsius) > 30
  ) {
    errors.temperature_celsius = "Must be between 15°C and 30°C.";
  }

  // Elevation, greater than 0, less than 2963 (integer)
  if (!form.elevation_m.trim()) {
    errors.elevation_m = "Elevation is required.";
  } else if (
    isNaN(Number(form.elevation_m)) ||
    !Number.isInteger(Number(form.elevation_m))
  ) {
    errors.elevation_m = "Must be a whole number.";
  } else if (Number(form.elevation_m) < 0 || Number(form.elevation_m) > 2963) {
    errors.elevation_m = "Must be between 0 and 2963 m.";
  }

  // pH, greater than 4.0, less than 8.5, 1 decimal place
  if (!form.ph.trim()) {
    errors.ph = "pH is required.";
  } else if (
    isNaN(Number(form.ph)) ||
    Number(form.ph) < 4.0 ||
    Number(form.ph) > 8.5
  ) {
    errors.ph = "Must be between 4.0 and 8.5.";
  }

  // Soil texture, required dropdown
  if (!form.soil_texture_id) {
    errors.soil_texture_id = "Soil texture is required.";
  }

  // Area, greater than 0, less than 100, 3 decimal places
  if (!form.area_ha.trim()) {
    errors.area_ha = "Area is required.";
  } else if (
    isNaN(Number(form.area_ha)) ||
    Number(form.area_ha) <= 0 ||
    Number(form.area_ha) > 100
  ) {
    errors.area_ha = "Must be between 0 and 100 ha.";
  }

  // Latitude, greater than -90, less than 90, 5 decimal places
  if (!form.latitude.trim()) {
    errors.latitude = "Latitude is required.";
  } else if (
    isNaN(Number(form.latitude)) ||
    Number(form.latitude) < -90 ||
    Number(form.latitude) > 90
  ) {
    errors.latitude = "Must be between -90 and 90.";
  }

  // Longitude, greater than -180, less than 180, 5 decimal places
  if (!form.longitude.trim()) {
    errors.longitude = "Longitude is required.";
  } else if (
    isNaN(Number(form.longitude)) ||
    Number(form.longitude) < -180 ||
    Number(form.longitude) > 180
  ) {
    errors.longitude = "Must be between -180 and 180.";
  }

  // Slope, greater than 0, less than 90, 2 decimal places
  if (!form.slope.trim()) {
    errors.slope = "Slope is required.";
  } else if (
    isNaN(Number(form.slope)) ||
    Number(form.slope) < 0 ||
    Number(form.slope) > 90
  ) {
    errors.slope = "Must be between 0 and 90 degrees.";
  }

  // Agroforestry types, required for register mode
  if (mode === "register" && form.agroforestry_type_ids.length === 0) {
    errors.agroforestry_type_ids = "Select at least one agroforestry type.";
  }

  return errors;
}
