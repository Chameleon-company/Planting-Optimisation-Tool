import { useState, useEffect } from "react";
import { Farm } from "@/hooks/useUserProfiles";
import { FarmUpdatePayload } from "@/hooks/useFarms";
import { AGROFORESTRY_TYPE_OPTIONS } from "@/components/farmManagement/farmForms/farmConstantsForm";
import { useSoilTextures } from "@/hooks/useSoilTextures";
// import { useAgroforestryTypes } from "@/hooks/useAgroforestryTypes";
import type {
  FormState,
  FormErrors,
} from "@/components/farmManagement/farmForms/farmConstantsForm";
import { validate } from "@/components/farmManagement/farmForms/validate";
import FarmFormFields from "@/components/farmManagement/farmForms/farmFormFields";

interface EditFarmFormProps {
  farm: Farm;
  onCancel: () => void;
  onSuccess: (farmId: number, payload: FarmUpdatePayload) => Promise<void>;
}

function getAgroforestryIds(farm: Farm): number[] {
  return farm.agroforestry_type
    .map(
      at =>
        AGROFORESTRY_TYPE_OPTIONS.find(
          opt => opt.name.toLowerCase() === at.type_name.toLowerCase()
        )?.id
    )
    .filter((id): id is number => id !== undefined);
}

export default function FarmEditForm({
  farm,
  onSuccess,
  onCancel,
}: EditFarmFormProps) {
  const { soilTextures, isLoading: soilTexturesLoading } = useSoilTextures();
  // const { agroforestryTypes, isLoading: agroforestryTypesLoading } = useAgroforestryTypes();

  // Set form as type formstate to what it currently says it is in the db
  const [form, setForm] = useState<FormState>({
    rainfall_mm: String(farm.rainfall_mm),
    temperature_celsius: String(farm.temperature_celsius),
    elevation_m: String(farm.elevation_m),
    ph: String(farm.ph),
    soil_texture_id: "",
    area_ha: String(farm.area_ha),
    latitude: String(farm.latitude),
    longitude: String(farm.longitude),
    coastal: farm.coastal,
    nitrogen_fixing: farm.nitrogen_fixing,
    shade_tolerant: farm.shade_tolerant,
    bank_stabilising: farm.bank_stabilising,
    slope: String(farm.slope),
    agroforestry_type_ids: getAgroforestryIds(farm),
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Add soil_texture_id into form once soilTextures have loaded
  useEffect(() => {
    const match = soilTextures.find(
      st => st.name.toLowerCase() === farm.soil_texture.name.toLowerCase()
    );
    if (match) {
      setForm(prev => ({ ...prev, soil_texture_id: String(match.id) }));
    }
  }, [soilTextures, farm.soil_texture.name]);

  // Sync agroforestry_type_ids into form once agroforestryTypes have loaded
  // useEffect(() => {
  //   const ids = getAgroforestryIds(farm, agroforestryTypes);
  //   setForm(prev => ({ ...prev, agroforestry_type_ids: ids }));
  // }, [agroforestryTypes]);

  // Function to update modal as user types in inputs, including typing and selecting elements
  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    // Set update form data, so all unselected values stay the same
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
    const fieldErrors = validate(form, "edit");
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
      await onSuccess(farm.id, {
        rainfall_mm: parseInt(form.rainfall_mm, 10),
        temperature_celsius: parseInt(form.temperature_celsius, 10),
        elevation_m: parseInt(form.elevation_m, 10),
        ph: parseFloat(form.ph),
        soil_texture_id: parseInt(form.soil_texture_id, 10),
        area_ha: parseFloat(form.area_ha),
        latitude: parseFloat(form.latitude),
        longitude: parseFloat(form.longitude),
        coastal: form.coastal,
        nitrogen_fixing: form.nitrogen_fixing,
        shade_tolerant: form.shade_tolerant,
        bank_stabilising: form.bank_stabilising,
        slope: parseFloat(form.slope),
        agroforestry_type_ids: form.agroforestry_type_ids,
      });
    } catch {
      setSubmitError("Failed to update farm. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form className="register-farm-form" onSubmit={handleSubmit} noValidate>
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
          className="btn-secondary"
          onClick={onCancel}
          disabled={isSubmitting}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="btn-primary"
          disabled={isSubmitting || soilTexturesLoading}
          // disabled={isSubmitting || soilTexturesLoading || agroforestryTypesLoading}
        >
          {isSubmitting ? "Saving…" : "Save changes"}
        </button>
      </div>
    </form>
  );
}
