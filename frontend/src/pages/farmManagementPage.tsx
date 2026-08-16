import { useState } from "react";
import { Helmet } from "react-helmet-async";
import { useAuth } from "@/contexts/AuthContext";
import {
  useFarms,
  FarmCreatePayload,
  FarmUpdatePayload,
} from "@/hooks/useFarms";
import { useUserProfiles, Farm } from "@/hooks/useUserProfiles";

import FarmsTable from "@/components/farmManagement/farmsTable";
import RegisterFarmModal from "@/components/farmManagement/farmRegisterModal";
import EditFarmModal from "@/components/farmManagement/farmsEditModal";
import FarmManageActions from "@/components/farmManagement/farmManagementEditButtons";
import FarmsHeader from "@/components/farmManagement/farmHeader";
import "./farmManagement.css";

export default function FarmsManagementPage() {
  // Call user, and create useState's for if the register modal is open, which farm is being edited,
  // and the current farmID being edited
  const { user } = useAuth();
  const [isRegisterModalOpen, setIsRegisterModalOpen] = useState(false);
  const [editingFarm, setEditingFarm] = useState<Farm | null>(null);
  const [selectedFarmId, setSelectedFarmId] = useState<number | null>(null);

  // Call variables as constants from useUserProfiles for refetching, and all relevant farm data
  const {
    farms,
    isLoading: farmsLoading,
    error: farmsError,
    page,
    setPage,
    totalFarms,
    totalPages,
    refetch,
  } = useUserProfiles();

  // Call variables from useFarms, mapping loading and error to new anme as they are constant
  // between useFarms and useUserProfiles, in this case the functions for mutation are needed
  const {
    isLoading: mutationLoading,
    error: mutationError,
    createFarm,
    updateFarm,
    deleteFarm,
  } = useFarms();

  // Function for if register is a sucesss if createFarm respondes positively
  // Then set the register Modal to closed and wait until farms list is refetched
  const handleRegisterSuccess = async (payload: FarmCreatePayload) => {
    const ok = await createFarm(payload);
    if (ok) {
      setIsRegisterModalOpen(false);
      await refetch();
    }
  };

  // If a farm has been selected, then find it in the farms with it's ID as key
  // if there's no farm, return, if found, set farm being edited to the farm with that ID
  const handleEditClick = () => {
    if (!selectedFarmId) {
      return;
    }
    const farm = farms.find(f => f.id === selectedFarmId);
    if (!farm) {
      return;
    }
    setEditingFarm(farm);
  };

  // If updateFarm method has returned true when handed ID and edited portion
  // Then, set editing modal to empty, and refetch farms list
  const handleEditSuccess = async (
    farmId: number,
    payload: FarmUpdatePayload
  ) => {
    const ok = await updateFarm(farmId, payload);
    if (ok) {
      setEditingFarm(null);
      await refetch();
    }
  };

  // If farm selected, await delete farm method, then clear selected farm ID and refetch
  const handleDelete = async () => {
    if (!selectedFarmId) return;
    const ok = await deleteFarm(selectedFarmId);
    if (ok) {
      setSelectedFarmId(null);
      await refetch();
    }
  };

  // Set error and isLoading as const var of farms error, and if not farms then mutation error
  // Or farms loading or mutation loading
  const error = farmsError ?? mutationError;
  const isLoading = farmsLoading || mutationLoading;

  return (
    <div className="farms-page">
      <Helmet>
        <title>Farm Management | Planting Optimisation Tool</title>
      </Helmet>

      <div className="page-header" style={{ position: "relative" }}>
        <FarmsHeader isLoading={farmsLoading} totalFarms={totalFarms} />
        <div
          style={{
            position: "absolute",
            right: "7%",
            top: "50%",
            transform: "translateY(-50%)",
          }}
        >
          <FarmManageActions
            onAdd={() => setIsRegisterModalOpen(true)}
            onEdit={handleEditClick}
            onDelete={handleDelete}
          />
        </div>
      </div>

      {error && <p className="farms-table-empty">{error}</p>}

      {/* Table to display conslidated farms data */}
      <FarmsTable
        farms={farms}
        isLoading={isLoading}
        user={user}
        page={page}
        totalPages={totalPages}
        setPage={setPage}
        selectedFarmId={selectedFarmId}
        onSelectFarm={setSelectedFarmId}
      />

      {/* Container for if Register new farm button is clicked */}
      {isRegisterModalOpen && (
        <RegisterFarmModal
          onClose={() => setIsRegisterModalOpen(false)}
          onSuccess={handleRegisterSuccess}
        />
      )}

      {/* Container for if Edit existing farm button is clicked */}
      {editingFarm && (
        <EditFarmModal
          farm={editingFarm}
          onClose={() => setEditingFarm(null)}
          onSuccess={handleEditSuccess}
        />
      )}
    </div>
  );
}
