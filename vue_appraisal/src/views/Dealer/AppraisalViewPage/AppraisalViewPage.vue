<template>
  <div class="dashboard-container">
    <div class="tabs">
      <!-- Appraisal tab (always shown) -->
      <button
        class="tab-button"
        :class="{ active: currentTab === 'appraisal' }"
        @click="currentTab = 'appraisal'"
      >
        Appraisal
      </button>

      <!-- Offers and Comments tabs (only shown if viewing an appraisal) -->
      <template v-if="isViewingAppraisal">
        <button
          v-if="isManagementDealer"
          class="tab-button"
          :class="{ active: currentTab === 'offers' }"
          @click="currentTab = 'offers'"
        >
          Offers
        </button>
        <button
          class="tab-button"
          :class="{ active: currentTab === 'comments' }"
          @click="currentTab = 'comments'"
        >
          Comments
        </button>
      </template>
    </div>

    <div v-if="currentTab === 'appraisal'">
      <div>
        <div v-if="isCreatingAppraisal" class="title-container">
          <h1 class="title">Create Appraisal Form</h1>
          <div class="checkbox-and-button">
            <label class="checkbox-container">
              <input
                type="checkbox"
                id="ready-for-management"
                v-model="formData.readyForManagement"
              />
              <span class="checkbox-label">Ready for Management</span>
            </label>
            <div class="notification-button" @click="submitForm">
              <span class="button-text">Create Appraisal</span>
            </div>
          </div>
        </div>

        <div v-else-if="isViewingAppraisal" class="title-container">
          <h1 class="title">View Appraisal Form</h1>
          <div class="checkbox-and-button">
            <!-- <button @click="duplicateAppraisal">Duplicate</button> -->
            <div class="duplicate-button" @click="duplicateAppraisal">
              <!-- <span class="button-text">Duplicate</span> -->
              <img src="@/assets/duplicate.svg" alt="Duplicate" />
            </div>
            <label class="checkbox-container">
              <input
                type="checkbox"
                id="is-active"
                v-model="appraisal.is_active"
              />
              <span class="checkbox-label">Active</span>
            </label>
            <label class="checkbox-container">
              <input
                type="checkbox"
                id="ready-for-management"
                v-model="appraisal.ready_for_management"
              />
              <span class="checkbox-label">Ready for Management</span>
            </label>
            <div class="notification-button" @click="updateAppraisal">
              <span class="button-text">Save Appraisal</span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="appraisal">
        <Appraisal>
          <template #header>
            <p class="headers">Customer Personal Details</p>
          </template>

          <!-- Client Details -->
          <template #customer-details>
            <div class="form-row">
              <input
                type="text"
                :placeholder="'First Name'"
                v-model="currentModel.customer_first_name"
              />
              <input
                type="text"
                :placeholder="'Last Name'"
                v-model="currentModel.customer_last_name"
              />
            </div>
            <div class="form-row">
              <input
                type="email"
                :placeholder="'Email'"
                v-model="currentModel.customer_email"
              />
              <div class="phone-input">
                <select>
                  <option
                    v-for="(code, country) in phoneCodes"
                    :key="code"
                    :value="code"
                  >
                    {{ code }} ({{ country }})
                  </option>
                </select>
                <input
                  type="text"
                  :placeholder="'Phone'"
                  v-model="currentModel.customer_phone"
                />
              </div>
            </div>
          </template>

          <!-- Initiating Dealer Pro -->
          <template #profile>
            <template v-if="isViewingAppraisal">
              <!-- Content for viewing an appraisal -->
              <p class="initiating-dealer">Initiating Dealer Pro</p>
              <p class="name">
                {{ appraisal.initiating_dealer?.first_name }}
                {{ appraisal.initiating_dealer?.last_name }}
              </p>
              <p class="last-updated-dealer">Last Updated Dealer</p>
              <p class="updated-name">
                {{ appraisal.last_updating_dealer?.first_name }}
                {{ appraisal.last_updating_dealer?.last_name }}
              </p>
              <div class="dealership-dropdown">
                <select class="input-dealership" v-model="selectedDealership">
                  <option disabled value="">Select Dealership</option>
                  <option
                    v-for="option in dealershipOptions"
                    :key="option.id"
                    :value="option.id"
                  >
                    {{ option.name }}
                  </option>
                </select>
              </div>
            </template>

            <template v-else-if="isCreatingAppraisal">
              <!-- Content for creating an appraisal -->
              <div class="profile-picture"></div>
              <p class="name">{{ userName }}</p>
              <p class="email">{{ userEmail }}</p>
              <div class="dealership-dropdown">
                <select class="input-dealership" v-model="selectedDealership">
                  <option disabled value="">Select Dealership</option>
                  <option
                    v-for="option in dealershipOptions"
                    :key="option.id"
                    :value="option.id"
                  >
                    {{ option.name }}
                  </option>
                </select>
              </div>
            </template>
          </template>

          <!-- Vehicle Details -->
          <template #basic-vehicle-details>
            <p class="headers">Basic Vehicle Details</p>
            <p class="small-header">Vehicle Make</p>
            <input
              type="text"
              v-model="currentModel.vehicle_make"
              placeholder="Car Make"
              class="input"
            />
            <p class="small-header">Vehicle Model</p>
            <input
              type="text"
              v-model="currentModel.vehicle_model"
              placeholder="Car Model"
              class="input"
            />
            <p class="small-header">Vehicle Year</p>
            <input
              type="text"
              v-model="currentModel.vehicle_year"
              placeholder="Car Year"
              class="input"
            />
            <p class="small-header">Vehicle Colour</p>
            <input
              type="text"
              v-model="currentModel.color"
              placeholder="Car Colour"
              class="input"
            />
            <p class="small-header">Vehicle Registration</p>
            <input
              type="text"
              v-model="currentModel.vehicle_registration"
              placeholder="Rego"
              class="input"
            />
            <p class="small-header">Vehicle VIN</p>
            <input
              type="text"
              v-model="currentModel.vehicle_vin"
              placeholder="VIN"
              class="input"
            />
          </template>

          <!-- Additional Details -->
          <template #advanced-vehicle-details>
            <p class="headers">Advanced Vehicle Details</p>

            <p class="small-header">Odometer Reading</p>
            <input
              type="text"
              placeholder="Odometer Reading"
              v-model="currentModel.odometer_reading"
              class="input"
            />

            <p class="small-header">Engine Type</p>
            <input
              type="text"
              placeholder="Engine Type"
              v-model="currentModel.engine_type"
              class="input"
            />

            <p class="small-header">Transmission</p>
            <select class="input" v-model="currentModel.transmission">
              <option
                v-for="option in transmissionOptions"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>

            <p class="small-header">Fuel Type</p>
            <select class="input" v-model="currentModel.fuel_type">
              <option
                v-for="option in fuelOptions"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>

            <p class="small-header">Body Type</p>
            <input
              type="text"
              placeholder="Body Type"
              v-model="currentModel.body_type"
              class="input"
            />

            <p class="small-header">Reserve Price</p>
            <div class="reserve-price-container">
              <div class="reserve-input-wrapper">
                <span class="reserve-icon">$</span>
                <input
                  type="text"
                  placeholder="Reserve Price"
                  v-model="currentModel.reserve_price"
                  class="reserve-input"
                />
              </div>
            </div>
          </template>

          <template #vehicle-damages>
            <div class="damages-header">
              <p class="headers">Vehicle Damages</p>
              <button @click="addDamage" class="add-damage-button">
                <img src="@/assets/add.svg" alt="Car Icon" class="car-icon" />
              </button>
            </div>
            <!-- if there are damages in appraisal.damages then display them in the inputs -->
            <div
              v-for="(damage, index) in damages"
              :key="index"
              class="damage-instance"
            >
              <p class="damage-label">{{ damageLabel(index) }}</p>
              <input
                type="text"
                v-model="damage.description"
                placeholder="Description"
                class="input"
              />
              <input
                type="text"
                v-model="damage.location"
                placeholder="Location"
                class="input"
              />
              <input
                type="text"
                v-model="damage.repair_cost_estimate"
                placeholder="Cost"
                class="input"
              />
              <button @click="removeDamage(index)" class="remove-damage-button">
                Remove
              </button>
            </div>
          </template>

          <template #car-pictures>
            <p class="headers">Car Pictures</p>
            <input
              type="file"
              id="photo-upload"
              multiple
              @change="handleFileUpload"
              class="upload-button"
            />
          </template>
        </Appraisal>
      </div>
      <div v-else>
        <p>There is no appraisal with this ID.</p>
      </div>
    </div>

    <div v-if="currentTab === 'offers'">
      <OfferTab :appraisal="appraisal" />
    </div>

    <div v-if="currentTab === 'comments'">
      <CommentTab :appraisal="appraisal" />
    </div>
  </div>
</template>

<script>
import Appraisal from "@/components/Appraisal.vue";
import CommentTab from "@/components/CommentTab.vue";
import OfferTab from "@/components/OfferTab.vue";
import { axiosInstance, endpoints } from "@/helpers/axiosHelper";
import { mapGetters } from "vuex";

export default {
  name: "AppraisalViewPage",
  components: {
    Appraisal,
    CommentTab,
    OfferTab,
  },
  computed: {
    ...mapGetters(["getUserProfile"]),
    userName() {
      const userProfile = this.getUserProfile;
      return userProfile
        ? `${userProfile.first_name} ${userProfile.last_name}`
        : "";
    },
    userEmail() {
      const userProfile = this.getUserProfile;
      return userProfile ? userProfile.email : "";
    },
    isCreatingAppraisal() {
      return this.$route.name === "CreateAppraisalPage";
    },
    currentModel() {
      return this.isViewingAppraisal
        ? this.appraisal || {}
        : this.formData || {};
    },
    isViewingAppraisal() {
      return this.$route.name === "AppraisalViewPage";
    },
    displayedPhotos() {
      return this.photos.slice(0, 4);
    },
    additionalPhotosCount() {
      return this.photos.length > 4 ? this.photos.length - 4 : 0;
    },
    isManagementDealer() {
      return this.formData && this.formData.role === "M";
    },
    isSalesDealer() {
      return this.formData && this.formData.role === "S";
    },
  },
  data() {
    return {
      selectedDealership: "",
      currentTab: "appraisal",
      dealershipOptions: [],
      damages: [],
      transmissionOptions: [
        { value: "", label: "Transmission" },
        { value: "Automatic", label: "Automatic" },
        { value: "Manual", label: "Manual" },
      ],
      fuelOptions: [
        { value: "", label: "Fuel Type" },
        { value: "Diesel", label: "Diesel" },
        { value: "Petrol", label: "Petrol" },
        { value: "Electric", label: "Electric" },
        { value: "Hybrid", label: "Hybrid" },
      ],
      showDropdown: false,
      showConfirmDialog: false,
      showAdjustInputPopup: false,
      selectedOffer: null,
      appraisal: {
        ready_for_management: false,
        damages: [],
        offers: [],
        winner: {},
        general_comments: [],
        private_comments: [],
      },
      phoneCodes: {
        "+61": "AU",
        "+1": "US",
        "+44": "UK",
      },
      photos: [],
      formData: {
        readyForManagement: false,
        customer_first_name: "",
        customer_last_name: "",
        customer_email: "",
        customer_phone: "",
        dealership: "",
        vehicle_make: "",
        vehicle_model: "",
        vehicle_year: "",
        color: "",
        vehicle_registration: "",
        odometer_reading: "",
        engine_type: "",
        transmission: "",
        fuel_type: "",
        body_type: "",
        reserve_price: "",
        damages: [],
        photos: [],
      },
    };
  },
  mounted() {
    this.fetchDealerProfileInfo();
  },
  created() {
    if (this.isViewingAppraisal) {
      this.fetchAppraisal();
    }
  },
  methods: {
    fetchAppraisal() {
      const id = this.$route.params.id;
      axiosInstance
        .get(`${endpoints.all_appraisals}${id}/`)
        .then((response) => {
          this.appraisal = response.data;
          this.damages = Array.isArray(this.appraisal.damages)
            ? this.appraisal.damages
            : [];
          this.appraisal.offers = Array.isArray(this.appraisal.offers)
            ? this.appraisal.offers
            : [];
        })
        .catch((error) => {
          console.error("Error fetching appraisal details:", error);
        });
    },

    selectDealership(dealership) {
      this.selectedDealership = dealership;
      this.formData.dealership = dealership.id;
      this.showDropdown = false;
    },
    damageLabel(index) {
      return `Damage ${index + 1}`;
    },
    removeDamage(index) {
      this.damages.splice(index, 1);
    },
    formatDate(dateString) {
      const options = { year: "numeric", month: "long", day: "numeric" };
      return new Date(dateString).toLocaleDateString(undefined, options);
    },
    async fetchDealerProfileInfo() {
      try {
        const response = await axiosInstance.get(endpoints.dealerProfile);
        this.formData = response.data;
        console.log("Dealer Profile Response:", response.data);
        // console log dealer profile role
        console.log("Dealer Profile Role:", response.data.role);

        const dealershipIds = response.data.dealerships || [];
        const dealershipNames = response.data.dealership_names || [];

        const dealershipMap = new Map(
          dealershipNames.map(({ id, dealership_name }) => [
            id,
            dealership_name,
          ])
        );

        this.dealershipOptions = dealershipIds.map((id) => ({
          id: id,
          name: dealershipMap.get(id) || `Dealership ${id}`,
        }));

        this.selectedDealership =
          this.dealershipOptions.length > 0 ? this.dealershipOptions[0].id : "";
      } catch (error) {
        console.error("Error fetching dealer profile information:", error);
      }
    },
    handleFileUpload(event) {
      const files = event.target.files;
      if (files.length > 0) {
        const newPhotos = Array.from(files).map((file) => ({
          url: URL.createObjectURL(file),
          name: file.name,
        }));
        this.photos = [...this.photos, ...newPhotos];
      }
    },
    handleDamageFileUpload(event, index) {
      const files = event.target.files;
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const reader = new FileReader();
        reader.onload = (e) => {
          this.damages[index].damagePhotos.push({ url: e.target.result });
        };
        reader.readAsDataURL(file);
      }
    },
    addDamage() {
      this.damages.push({
        description: "",
        location: "",
        repair_cost_estimate: "",
        damagePhotos: [],
      });
    },
    async duplicateAppraisal() {
      const id = this.$route.params.id; // Get the current appraisal ID from the route
      try {
        const response = await axiosInstance.post(
          endpoints.duplicateAppraisal(id)
        );
        this.$router.push({
          name: "AppraisalViewPage",
          params: { id: response.data.id },
        });
        console.log("Appraisal duplicated successfully:", response.data);
      } catch (error) {
        console.error("Error duplicating appraisal:", error);
      }
    },

    updateAppraisal() {
      // Check if there are existing offers
      if (this.appraisal.offers.length > 0) {
        // Display a pop-up message
        alert("Offers exist, so the appraisal cannot be updated.");
        return; // Exit the function to prevent further execution
      }

      const id = this.$route.params.id;
      const data = {
        ready_for_management: this.appraisal.ready_for_management,
        customer_first_name: this.appraisal.customer_first_name,
        customer_last_name: this.appraisal.customer_last_name,
        customer_email: this.appraisal.customer_email,
        customer_phone: this.appraisal.customer_phone,
        vehicle_make: this.appraisal.vehicle_make,
        vehicle_model: this.appraisal.vehicle_model,
        vehicle_year: this.appraisal.vehicle_year,
        color: this.appraisal.color,
        vehicle_registration: this.appraisal.vehicle_registration,
        odometer_reading: this.appraisal.odometer_reading,
        engine_type: this.appraisal.engine_type,
        transmission: this.appraisal.transmission,
        body_type: this.appraisal.body_type,
        fuel_type: this.appraisal.fuel_type,
        reserve_price: this.appraisal.reserve_price,
        is_active: this.appraisal.is_active,
        photos: this.photos.map((photo) => photo.url),
        damages: this.damages.map((damage) => ({
          description: damage.description,
          location: damage.location,
          repair_cost_estimate: parseInt(damage.repair_cost_estimate, 10),
        })),
        // Include other fields you need to update here
      };

      axiosInstance
        .patch(`${endpoints.all_appraisals}${id}/`, data)
        .then((response) => {
          this.appraisal = response.data;
          this.$emit("appraisal-updated", response.data);
          console.log("Appraisal updated successfully:", response.data);
        })
        .catch((error) => {
          console.error("Error updating appraisal:", error);
        });
    },

    async submitForm() {
      try {
        const data = {
          dealership: this.selectedDealership,
          ready_for_management: this.formData.readyForManagement,
          customer_first_name: this.formData.customer_first_name,
          customer_last_name: this.formData.customer_last_name,
          customer_email: this.formData.customer_email,
          customer_phone: this.formData.customer_phone,
          vehicle_make: this.formData.vehicle_make,
          vehicle_model: this.formData.vehicle_model,
          vehicle_year: parseInt(this.formData.vehicle_year, 10),
          vehicle_vin: this.formData.vehicle_vin || "",
          vehicle_registration: this.formData.vehicle_registration,
          color: this.formData.color,
          odometer_reading: parseInt(this.formData.odometer_reading, 10),
          engine_type: this.formData.engine_type,
          transmission: this.formData.transmission,
          body_type: this.formData.body_type,
          fuel_type: this.formData.fuel_type,
          reserve_price: parseInt(this.formData.reserve_price, 10),
          damages: this.damages.map((damage) => ({
            description: damage.description,
            location: damage.location,
            repair_cost_estimate: parseInt(damage.repair_cost_estimate, 10),
          })),
          photos: this.photos.map((photo) => photo.url),
        };

        if (this.isCreatingAppraisal) {
          await axiosInstance.post(endpoints.all_appraisals, data);
          this.$router.push({ name: "AppraisalListPage" });
        } else if (this.isViewingAppraisal) {
          await this.updateAppraisal();
        }
      } catch (error) {
        console.error("Error submitting form:", error);
      }
    },
  },
};
</script>

<style scoped>
.dashboard-container {
  margin-left: auto;
  margin-right: auto;
  max-width: 1200px;
  padding: 20px;
  box-sizing: border-box;
}

.title-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.checkbox-and-button {
  display: flex;
  align-items: center;
}

.checkbox-container {
  display: flex;
  align-items: center;
  margin-right: 20px; /* Space between checkbox and button */
}

.checkbox-container input[type="checkbox"] {
  margin-right: 10px; /* Space between checkbox and label */
}

.checkbox-label {
  font-size: 14px; /* Adjust font size as needed */
  font-weight: 400;
}

.notification-button {
  width: 150px; /* Adjust width to fit text */
  height: 40px;
  border-radius: 20px; /* Rounded corners for button */
  background-color: #f26764;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 14px; /* Adjust font size */
  font-weight: 600;
  color: #ffffff; /* Text color */
  text-align: center;
  border: 4px solid white;
  border-radius: 50px;
}

.duplicate-button {
  width: 40px; /* Adjust width to fit text */
  height: 40px;
  border-radius: 20px; /* Rounded corners for button */
  background-color: #f26764;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 14px; /* Adjust font size */
  font-weight: 600;
  color: #ffffff; /* Text color */
  text-align: center;
  border: 4px solid white;
  border-radius: 50px;
  margin-right: 20px;
}

.button-text {
  padding: 0 10px; /* Adjust padding as needed */
}

.title {
  font-size: 24px;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  font-weight: 200;
  font-weight: 600;
}

.name {
  margin: 0;
}
.email {
  color: #7d7b7b;
  font-size: 12px;
}

.appraisals-listings {
  width: 75%;
  background-color: #ffffff;
}

.headers {
  font-size: 16px;
  font-weight: 400;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  font-weight: 600;
  padding-left: 10px;
}

.form-row {
  display: flex;
  gap: 20px;
  width: 100%;
}

.phone-input {
  display: flex;
  gap: 10px;
  width: 100%;
}

.phone-input input[type="text"] {
  width: 70%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
  box-sizing: border-box;
}

/* dealership button */
.dealership-dropdown {
  position: relative;
  display: inline-block;
}

.dealership-dropdown button {
  padding: 8px 16px;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  font-weight: 400;
  font-size: 12px;
  border: none;
  border-radius: 5px;
  background-color: #ffffff;
  border: 1px solid #000000;
  color: #000000;
  cursor: pointer;
  width: 100%;
}

.dropdown-content {
  display: block;
  position: absolute;
  background-color: #f9f9f9;
  box-shadow: 0px 8px 16px 0px rgba(0, 0, 0, 0.2);
  z-index: 1;
  border-radius: 5px;
  margin-top: 8px;
  width: 100%;
  font-size: 11px;
}

.dropdown-content p {
  color: black;
  padding: 5px;
  text-decoration: none;
  display: block;
  cursor: pointer;
}

.dropdown-content p:hover {
  background-color: #f1f1f1;
}

.input {
  margin-bottom: 20px;
  margin-left: 10px;
}

.input-dealership {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  font-weight: 400;
  font-size: 12px;
  border: none;
  border-radius: 5px;
  background-color: #ffffff;
  border: 1px solid #000000;
  width: 100%;
  color: #000000;
  cursor: pointer;
  text-align: center;
}

input[type="text"],
input[type="email"],
select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
  box-sizing: border-box;
  width: 95%;
  height: 39px;
}

input[type="text"],
input[type="email"] {
  /* Ensure these fields have the same height */
  height: 39px; /* Adjust as necessary to match your design */
}

select {
  width: 95%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
  box-sizing: border-box;
  height: 39px;
  -webkit-appearance: none; /* Remove default styles in WebKit browsers */
  -moz-appearance: none; /* Remove default styles in Firefox */
  appearance: none; /* Remove default styles */
  background: white; /* Ensure the background color matches */
}

#photo-upload {
  margin-bottom: 10px;
}

.profile-picture {
  height: 65px;
  width: 65px;
  border-radius: 50%;
  background-color: #e7e7e7;
  margin-bottom: 10px;
}

.photo-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #e7e7e7;
  color: #ffffff;
  font-size: 24px;
  font-weight: bold;
}

.more-photos {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background-color: rgba(0, 0, 0, 0.5);
  color: #ffffff;
  border-radius: 5px;
  padding: 5px;
  font-size: 14px;
}

.upload-button {
  padding: 10px;
  font-size: 14px;
}

.add-damage-button {
  width: 30px; /* Size of the button */
  height: 30px; /* Size of the button */
  border-radius: 50%; /* Makes the button circular */
  background-color: #f26764; /* Button background color */
  border: none; /* Remove default border */
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  margin-right: 10px;
}

.add-damage-button img {
  width: 20px; /* Size of the icon */
  height: 20px; /* Size of the icon */
}

.info-text {
  margin: 10px 0;
  font-size: 14px;
  text-align: center;
}

.input {
  width: calc(100% - 22px); /* Adjust based on your design */
}

.damages-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px; /* Adjust as needed */
}

.remove-damage-button {
  background-color: #f26764; /* Button background color */
  border: none; /* Remove default border */
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 10px;
  margin-right: 10px;
  border-radius: 10px;
  margin-left: 10px;
  color: #ffffff;
  margin-bottom: 10px;
  font-weight: 500;
}

.small-header {
  font-size: 12px;
  color: #7d7b7b;
  padding-left: 10px;
  margin-top: 0;
  font-weight: 600;
}

.reserve-price-container {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  width: 100%; /* Ensure the container takes full width */
}

.reserve-input-wrapper {
  position: relative;
  width: 100%; /* Ensure the wrapper takes full width */
}

.reserve-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none; /* Prevents the icon from blocking input interaction */
  color: #000; /* Adjust the color as needed */
  font-size: 14px; /* Adjust the size as needed */
}

.reserve-input {
  width: 100%;
  padding-left: 30px; /* Add padding to make space for the icon */
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
  box-sizing: border-box;
  height: 39px;
  margin-left: 30px;
  margin-right: 10px;
}

/* Specific styling for reserve input to override generic input styles */
input.reserve-input {
  width: calc(95% - 20px); /* Adjust width to account for padding */
  padding-right: 10px;
  height: 39px;
  border: 1px solid #ddd;
  border-radius: 5px;
  box-sizing: border-box;
}

.damage-label {
  padding-left: 10px;
  font-weight: 600;
  color: #7d7b7b;
}

.error-message {
  color: red;
  font-size: 11px;
}

.initiating-dealer {
  font-size: 10px;
  color: #7d7b7b;
  margin-top: 0;
}

.updated-name {
  margin-top: 0;
}

.last-updated-dealer {
  font-size: 10px;
  color: #7d7b7b;
  margin-top: 30px;
}

/* Tabs */
.tabs {
  display: flex;
  margin-bottom: 20px;
  position: relative;
  padding-left: 0;
  padding-right: 0;
  justify-content: flex-start; /* Align tabs to the left */
}

.tab-button {
  background-color: transparent;
  border: none;
  padding: 10px 20px; /* Adjust padding as needed */
  margin-right: 10px; /* Add space between buttons */
  cursor: pointer;
  font-size: 12px;
  text-align: center;
  color: #b0b0b0;
  position: relative;
}

.tab-button.active {
  color: #333;
  font-weight: 600;
}

.tab-button::after {
  content: "";
  display: block;
  height: 2px;
  background-color: #eb5a58;
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  transform: scaleX(0);
  transform-origin: bottom left;
  transition: transform 0.3s ease;
}

.tab-button.active::after {
  transform: scaleX(1);
}
</style>
