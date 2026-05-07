import { useState } from "react";
import { FarmCreatePayload } from "@/hooks/useFarms";
import { AGROFORESTRY_TYPE_OPTIONS } from "@/components/farmManagement/farmForms/farmConstantsForm";
import { useSoilTextures } from "@/hooks/useSoilTextures";
// import { useAgroforestryTypes } from "@/hooks/useAgroforestryTypes";
import type {
  FormState,
  FormErrors,
} from "@/components/farmManagement/farmForms/farmConstantsForm";
import { validate } from "@/components/farmManagement/farmForms/validate";
import FarmFormFields from "@/components/farmManagement/farmForms/farmFormFields";

interface RegisterFarmFormProps {
  onCancel: () => void;
  onSuccess: (payload: FarmCreatePayload) => Promise<void>;
}

// Inital state for register form, basically make fields empty and false by default
const INITIAL_STATE: FormState = {
  rainfall_mm: "",
  temperature_celsius: "",
  elevation_m: "",
  ph: "",
  soil_texture_id: "",
  area_ha: "",
  latitude: "",
  longitude: "",
  coastal: false,
  nitrogen_fixing: false,
  shade_tolerant: false,
  bank_stabilising: false,
  slope: "",
  agroforestry_type_ids: [],
};

export default function RegisterFarmForm({
  onSuccess,
  onCancel,
}: RegisterFarmFormProps) {
  const { soilTextures, isLoading: soilTexturesLoading } = useSoilTextures();
  // const { agroforestryTypes, isLoading: agroforestryTypesLoading } = useAgroforestryTypes();

  const [form, setForm] = useState<FormState>(INITIAL_STATE);
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Function to update modal as user types in inputs, including typing and selecting elements
  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    // Get name and value from event target
    const { name, value } = e.target;
    // Set create form data, so all unselected values stay the same
    // and only the value with name as a key, will change to current value
    setForm(prev => ({ ...prev, [name]: value }));
    // If an error is occuring, and the error no longer occurs as of handle change, or a new one
    // Appears, then change the error
    if (errors[name as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  const handleAgroforestryToggle = (id: number) => {
    // Create new object from prev
    setForm(prev => {
      // Create var that contains all existing agrofor types already
      const already = prev.agroforestry_type_ids.includes(id);
      return {
        // return new coped object from prev, where either an id is removed from already
        // or a new one is added
        ...prev,
        agroforestry_type_ids: already
          ? prev.agroforestry_type_ids.filter(x => x !== id) // This branch removes
          : [...prev.agroforestry_type_ids, id], // this one adds
      };
    });
    // Reset errors as changes
    if (errors.agroforestry_type_ids) {
      setErrors(prev => ({ ...prev, agroforestry_type_ids: undefined }));
    }
  };

  // Set new form from prev, only allowing those four names as booleans
  const handleBooleanToggle = (
    name: "coastal" | "nitrogen_fixing" | "shade_tolerant" | "bank_stabilising"
  ) => {
    // Create new object where we flip prev from name, so false becomes true
    setForm(prev => ({ ...prev, [name]: !prev[name] }));
  };

  // on submit
  const handleSubmit = async (e: React.SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();
    // use validate.ts to check that the form is fine with the backend
    const fieldErrors = validate(form, "register");
    // If errors found set errors to that
    if (Object.keys(fieldErrors).length > 0) {
      setErrors(fieldErrors);
      return;
    }

    setIsSubmitting(true);
    setSubmitError(null);

    // Try catch, call on success, and hand fields to it as payload
    // with elements parsed as their correct types
    try {
      await onSuccess({
        rainfall_mm: parseInt(form.rainfall_mm, 10),
        temperature_celsius: parseInt(form.temperature_celsius, 10),
        elevation_m: parseInt(form.elevation_m, 10),
        ph: parseFloat(form.ph),
        soil_texture_id: parseInt(form.soil_texture_id, 10),
        area_ha: parseFloat(form.area_ha),
        latitude: parseFloat(form.latitude),
        longitude: parseFloat(form.longitude),
        coastal: form.coastal,
        riparian: false,
        nitrogen_fixing: form.nitrogen_fixing,
        shade_tolerant: form.shade_tolerant,
        bank_stabilising: form.bank_stabilising,
        slope: parseFloat(form.slope),
        agroforestry_type_ids: form.agroforestry_type_ids,
      });
    } catch {
      setSubmitError("Failed to register farm. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form className="register-farm-form" onSubmit={handleSubmit} noValidate>
      {/* Display form fields */}
      <FarmFormFields
        form={form}
        errors={errors}
        isSubmitting={isSubmitting || soilTexturesLoading}
        // isSubmitting={isSubmitting || soilTexturesLoading || agroforestryTypesLoading}
        onChange={handleChange}
        onAgroforestryToggle={handleAgroforestryToggle}
        onBooleanToggle={handleBooleanToggle}
        soilTextures={soilTextures}
        agroforestryTypes={AGROFORESTRY_TYPE_OPTIONS}
        // agroforestryTypes={agroforestryTypes}
      />

      {submitError && (
        <p className="register-farm-submit-error">{submitError}</p>
      )}

      <div className="register-farm-actions">
        <button
          type="button"
          className="register-farm-btn register-farm-btn-secondary"
          onClick={onCancel}
          disabled={isSubmitting}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="register-farm-btn register-farm-btn-primary"
          disabled={isSubmitting || soilTexturesLoading}
          // disabled={isSubmitting || soilTexturesLoading || agroforestryTypesLoading}
        >
          {isSubmitting ? "Registering…" : "Register farm"}
        </button>
      </div>
    </form>
  );
}
