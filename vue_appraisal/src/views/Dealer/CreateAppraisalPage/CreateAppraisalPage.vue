<template>
  <div class="dashboard-container">
    <div class="title-container">
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

    <div class="columns-container">
      <div class="column column-60">
        <div class="greetings-container">
          <p class="headers">Customer Personal Details</p>
          <form class="customer-details-form">
            <div class="form-row">
              <input
                type="text"
                placeholder="First Name"
                v-model="formData.firstName"
              />
              <input
                type="text"
                placeholder="Last Name"
                v-model="formData.lastName"
              />
            </div>
            <div class="form-row">
              <input
                type="email"
                placeholder="Email"
                v-model="formData.email"
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
                  placeholder="Phone"
                  v-model="formData.appraisal_phone"
                />
              </div>
            </div>
          </form>
        </div>
      </div>

      <div class="column column-40">
        <div class="profile-container">
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
        </div>
      </div>
    </div>

    <div class="appraisals-container">
      <div class="appraisals">
        <p class="headers">Basic Vehicle Details</p>
        <p class="small-header">Vehicle Make</p>
        <input
          type="text"
          placeholder="Vehicle Make"
          v-model="formData.vehicleMake"
          class="input"
        />
        <p class="small-header">Vehicle Model</p>
        <input
          type="text"
          placeholder="Vehicle Model"
          v-model="formData.vehicleModel"
          class="input"
        />
        <p class="small-header">Vehicle Year</p>
        <input
          type="text"
          placeholder="Vehicle Year"
          v-model="formData.vehicleYear"
          class="input"
        />
        <p class="small-header">Vehicle Colour</p>
        <input
          type="text"
          placeholder="Vehicle Colour"
          v-model="formData.vehicleColour"
          class="input"
        />
        <p class="small-header">Vehicle Registration</p>
        <input
          type="text"
          placeholder="Vehicle Registration Number"
          v-model="formData.vehicleRegistration"
          class="input"
        />
        <p class="small-header">VIN</p>
        <input
          type="text"
          placeholder="VIN"
          v-model="formData.vehicleVin"
          class="input"
        />
      </div>

      <div class="stats-container">
        <div class="stats other-stats">
          <p class="headers">Advanced Vehicle Details</p>
          <p class="small-header">Odometer Reading</p>
          <input
            type="text"
            placeholder="Odometer Reading"
            v-model="formData.odometerReading"
            class="input"
          />
          <p class="small-header">Engine Type</p>
          <input
            type="text"
            placeholder="Engine Type"
            v-model="formData.engineType"
            class="input"
          />
          <p class="small-header">Transmission</p>
          <select class="input" v-model="formData.transmission">
            <option
              v-for="option in transmissionOptions"
              :key="option.value"
              :value="option.value"
            >
              {{ option.label }}
            </option>
          </select>
          <p class="small-header">Fuel Type</p>
          <select class="input" v-model="formData.fuelType">
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
            v-model="formData.bodyType"
            class="input"
          />
          <p class="small-header">Reserve Price</p>
          <div class="reserve-price-container">
            <div class="reserve-input-wrapper">
              <span class="reserve-icon">$</span>
              <input
                type="text"
                placeholder="Reserve Price"
                v-model="formData.reservePrice"
                class="reserve-input"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add more sections as needed -->
    <div class="appraisals-container">
      <div class="appraisals">
        <div class="damages-header">
          <p class="headers">Vehicle Damages</p>
          <button @click="addDamage" class="add-damage-button">
            <img src="@/assets/add.svg" alt="Car Icon" class="car-icon" />
          </button>
        </div>
        <div
          v-for="(damage, index) in damages"
          :key="index"
          class="damage-instance"
        >
          <p class="damage-label">{{ damageLabel(index) }}</p>
          <input
            v-model="damage.description"
            type="text"
            placeholder="Damage Description"
            class="input"
          />
          <input
            v-model="damage.location"
            type="text"
            placeholder="Damage Location"
            class="input"
          />
          <input
            v-model="damage.repairCost"
            type="text"
            placeholder="Damage Repair Cost"
            class="input"
          />
          <input
            type="file"
            :id="'damage-photo-upload-' + index"
            multiple
            @change="handleDamageFileUpload($event, index)"
            class="upload-button"
          />
          <div class="photos-preview">
            <div
              v-for="(photo, photoIndex) in damage.damagePhotos.slice(0, 4)"
              :key="photoIndex"
              class="photo-container"
            >
              <img :src="photo.url" v-if="photo.url" class="photo-preview" />
              <div v-else class="photo-placeholder">+</div>
            </div>
            <div v-if="damage.damagePhotos.length > 4" class="more-photos">
              {{ damage.damagePhotos.length - 4 }}+
            </div>
          </div>
          <button @click="removeDamage(index)" class="remove-damage-button">
            Remove
          </button>
        </div>
      </div>

      <div class="appraisals-photos">
        <p class="headers">Car Pictures</p>
        <input
          type="file"
          id="photo-upload"
          multiple
          @change="handleFileUpload"
          class="upload-button"
        />
        <div class="photos-preview">
          <div
            v-for="(photo, index) in displayedPhotos"
            :key="index"
            class="photo-container"
          >
            <img :src="photo.url" v-if="photo.url" class="photo-preview" />
            <div v-else class="photo-placeholder">+</div>
          </div>
          <div v-if="additionalPhotosCount > 0" class="more-photos">
            {{ additionalPhotosCount }}+
          </div>
        </div>
      </div>
    </div>
    <ToastNotification
      :message="toastMessage"
      :visible="showToast"
      @update:visible="showToast = $event"
    />
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import { axiosInstance, endpoints } from "@/helpers/axiosHelper";
import ToastNotification from "@/components/ToastNotification.vue";

export default {
  name: "CreateAppraisalPage",
  components: {
    ToastNotification,
  },
  computed: {
    ...mapGetters(["getUserProfile"]),
    userName() {
      const userProfile = this.getUserProfile;
      return userProfile
        ? `${userProfile.first_name} ${userProfile.last_name}`
        : "Guest";
    },
    userEmail() {
      const userProfile = this.getUserProfile;
      return userProfile ? userProfile.email : "";
    },
    displayedPhotos() {
      return this.photos.slice(0, 4); // Show only up to 4 images
    },
    additionalPhotosCount() {
      return this.photos.length > 4 ? this.photos.length - 4 : 0; // Number of additional photos
    },
  },
  data() {
    return {
      showDropdown: false,
      showToast: false,
      toastMessage: "",
      selectedDealership: "",
      dealershipOptions: [], // Initially empty
      phoneCodes: {
        "+61": "AU",
        "+1": "US",
        "+44": "UK",
      },
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
      photos: [], // Array to store the uploaded photos
      damages: [], // Array to store damage instances
      formData: {
        readyForManagement: false,
        firstName: "",
        lastName: "",
        email: "",
        appraisal_phone: "",
        dealership: "",
        vehicleMake: "",
        vehicleModel: "",
        vehicleYear: "",
        vehicleColour: "",
        vehicleRegistration: "",
        odometerReading: "",
        engineType: "",
        transmission: "",
        fuelType: "",
        bodyType: "",
        reservePrice: "",
        damages: [],
        photos: [],
      },
    };
  },
  mounted() {
    this.fetchDealerProfileInfo();
  },
  methods: {
    toggleDropdown() {
      this.showDropdown = !this.showDropdown;
    },
    selectDealership(dealership) {
      this.selectedDealership = dealership;
      this.formData.dealership = dealership.id; // Set the ID of the selected dealership in formData
      this.showDropdown = false;
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
        repairCost: "",
        damagePhotos: [],
      });
    },
    removeDamage(index) {
      this.damages.splice(index, 1);
    },
    damageLabel(index) {
      return `Damage ${index + 1}`;
    },
    async fetchDealerProfileInfo() {
      try {
        // Fetch dealer profile info
        const response = await axiosInstance.get(endpoints.dealerProfile);
        this.formData = response.data;

        // Extract dealership IDs and names from the response
        const dealershipIds = response.data.dealerships || []; // Ensure it's an array
        const dealershipNames = response.data.dealership_names || []; // Ensure it's an array

        // Create a map of dealership IDs to names for easy lookup
        const dealershipMap = new Map(
          dealershipNames.map(({ id, dealership_name }) => [
            id,
            dealership_name,
          ])
        );

        // Populate dealershipOptions with dealership names based on the IDs
        this.dealershipOptions = dealershipIds.map((id) => ({
          id: id,
          name: dealershipMap.get(id) || `Dealership ${id}`, // Fallback to `Dealership ${id}` if name is not found
        }));

        // Set the selectedDealership based on the first dealership option, if applicable
        this.selectedDealership =
          this.dealershipOptions.length > 0 ? this.dealershipOptions[0].id : "";
      } catch (error) {
        console.error("Error fetching dealer profile information:", error);
      }
    },
    async submitForm() {
      try {
        // Prepare form data for submission
        const data = {
          dealership: this.selectedDealership, // Use the selected dealership ID
          ready_for_management: this.formData.readyForManagement,
          customer_first_name: this.formData.firstName,
          customer_last_name: this.formData.lastName,
          customer_email: this.formData.email,
          customer_phone: this.formData.phone,
          vehicle_make: this.formData.vehicleMake,
          vehicle_model: this.formData.vehicleModel,
          vehicle_year: parseInt(this.formData.vehicleYear, 10), // Convert to integer
          vehicle_vin: this.formData.vehicleVin || "", // Provide a default if this field is optional
          vehicle_registration: this.formData.vehicleRegistration,
          color: this.formData.vehicleColour,
          odometer_reading: parseInt(this.formData.odometerReading, 10), // Convert to integer
          engine_type: this.formData.engineType,
          transmission: this.formData.transmission,
          body_type: this.formData.bodyType,
          fuel_type: this.formData.fuelType,
          reserve_price: parseInt(this.formData.reservePrice, 10), // Convert to integer
          damages: this.damages.map((damage) => ({
            damage_description: damage.description,
            damage_location: damage.location,
            repair_cost_estimate: parseInt(damage.repairCost, 10), // Convert to integer
          })),
          photos: this.photos.map((photo) => photo.url), // Ensure this matches backend expectations
        };

        console.log("Submitting data:", data); // Debug output

        // Make POST request to create appraisal
        const response = await axiosInstance.post(
          endpoints.createAppraisal,
          data
        );
        console.log("Appraisal created successfully", response.data);

        this.toastMessage = "Appraisal created successfully";
        this.showToast = true;
        // Handle successful submission, e.g., redirect or show a success message
      } catch (error) {
        console.error("Error creating appraisal:", error);
        this.toastMessage = "Error creating appraisal";
        this.showToast = true;
        // Handle error, e.g., show an error message
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

.columns-container {
  display: flex;
  margin: 20px 0;
  gap: 20px;
}

.column {
  padding: 10px;
  box-sizing: border-box;
  height: 210px;
  border-radius: 10px;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
  transition: 0.3s;
}

.column-60 {
  width: 75%;
  background-color: #ffffff;
}

.column-40 {
  width: 25%;
  background-color: #ffffff;
}

.profile-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 10px;
  margin: 0;
  font-size: 16px;
  font-weight: 400;
}

.profile-picture {
  height: 70px;
  width: 70px;
  border-radius: 50%;
  background-color: #e7e7e7;
  margin-bottom: 10px;
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

.greetings-container {
  width: 100%;
  padding: 10px;
  margin: 0;
}

.customer-details-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-right: 20px;
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

.appraisals-container {
  display: flex;
  margin: 20px 0;
  gap: 20px;
}

.appraisals {
  width: 50%;
  background-color: #ffffff;
  padding: 10px;
  box-sizing: border-box;
  border-radius: 10px;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
  height: 100%; /* Make sure the height adjusts with the content */
}

.appraisals-photos {
  width: 50%;
  background-color: #ffffff;
  padding: 10px;
  box-sizing: border-box;
  border-radius: 10px;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
  height: 100%; /* Make sure the height adjusts with the content */
}

.stats-container {
  width: 50%;
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%; /* Make sure the height adjusts with the content */
}

.stats {
  background-color: #ffffff;
  padding: 10px;
  box-sizing: border-box;
  border-radius: 10px;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
  flex: 1; /* Ensure stats containers grow to the same height */
}

.other-stats {
  flex: 1;
}

.appraisals-photos {
  background-color: #ffffff;
  padding: 10px;
  box-sizing: border-box;
  border-radius: 10px;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
  height: 100%; /* Adjust height as necessary */
  position: relative;
}

#photo-upload {
  margin-bottom: 10px;
}

.photos-preview {
  display: flex;
  gap: 20px;
  margin-bottom: 10px;
  padding-left: 10px;
}

.photo-container {
  position: relative;
  width: 100px; /* Adjust size as needed */
  height: 100px; /* Adjust size as needed */
  overflow: hidden;
  border-radius: 5px;
}

.photo-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
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
</style>
