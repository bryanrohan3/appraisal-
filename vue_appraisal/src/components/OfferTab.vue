<template>
  <div class="offers-container">
    <table class="offers-table" v-if="appraisal.offers.length > 0">
      <thead>
        <tr class="offers-table-header">
          <th>Offer ID</th>
          <th>User Info</th>
          <th>Created At</th>
          <th>Offer Amount</th>
          <th>Offer Made At</th>
          <th>Adjusted Amount</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="offer in appraisal.offers"
          :key="offer.id"
          @click="toggleDropdown(offer.id)"
          :class="{
            'winning-row': offer.id === appraisal.winner?.offer_id,
          }"
        >
          <td>{{ offer.id }}</td>
          <td>
            <strong>
              {{ offer.user?.first_name }} {{ offer.user?.last_name }}
            </strong>
            <br />
            <span>@{{ offer.user?.username }}</span>
          </td>
          <td>
            {{ offer.created_at ? formatDate(offer.created_at) : "null" }}
          </td>
          <td>{{ offer.amount !== null ? `$${offer.amount}` : "null" }}</td>
          <td>
            {{ offer.offer_made_at ? formatDate(offer.offer_made_at) : "null" }}
          </td>
          <td>
            {{
              offer.adjusted_amount !== null
                ? `$${offer.adjusted_amount}`
                : "null"
            }}
          </td>
          <td class="actions-cell">
            <img src="@/assets/dots.svg" alt="Actions" class="actions-icon" />
            <div v-if="offer.showDropdown" class="dropdown-menu">
              <button @click.stop="triggerConfirmDialog(offer.id)">
                Select Winner
              </button>

              <button @click.stop="showAdjustInput(offer)">
                Adjust Amount
              </button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-else class="no-offers-message">No offers available.</div>

    <div v-if="showConfirmDialog" class="confirm-dialog">
      <p>Are you sure you want to select this offer as the winner?</p>
      <button @click="confirmSelection">Yes</button>
      <button @click="cancelSelection">No</button>
    </div>

    <div v-if="showAdjustInputPopup" class="adjust-offer-popup">
      <label for="adjusted-offer-input">Adjusted Offer:</label>
      <input
        type="number"
        id="adjusted-offer-input"
        v-model="selectedOffer.adjusted_amount"
        class="adjusted-offer-input"
        placeholder="Enter adjusted offer"
      />
      <button
        class="submit-offer-button"
        @click="
          submitAdjustedOffer(selectedOffer.id, selectedOffer.adjusted_amount)
        "
      >
        Submit
      </button>
      <button class="cancel-offer-button" @click="cancelAdjustInput">
        Cancel
      </button>
    </div>
  </div>
</template>

<script>
import { axiosInstance, endpoints } from "@/helpers/axiosHelper";

export default {
  name: "OfferTab",
  props: {
    appraisal: {
      type: Object,
      required: true,
      default: () => ({
        offers: [], // Ensure `offers` is an array
        winner: {},
      }),
    },
  },
  data() {
    return {
      showDropdown: false,
      showConfirmDialog: false,
      showAdjustInputPopup: false,
      selectedOffer: null,
    };
  },
  computed: {
    activeOffers() {
      return this.appraisal.offers.filter((offer) => !offer.archived);
    },
    archivedOffers() {
      return this.appraisal.offers.filter((offer) => offer.archived);
    },
  },
  methods: {
    formatDate(dateString) {
      const options = { year: "numeric", month: "short", day: "numeric" };
      return new Date(dateString).toLocaleDateString(undefined, options);
    },
    toggleDropdown(offerId) {
      const offer = this.appraisal.offers.find((o) => o.id === offerId);
      if (offer) {
        offer.showDropdown = !offer.showDropdown;
        // Close any open dropdowns if clicking elsewhere
        this.appraisal.offers.forEach((o) => {
          if (o.id !== offerId) o.showDropdown = false;
        });
      }
    },
    showAdjustInput(offer) {
      this.selectedOffer = offer;
      this.showAdjustInputPopup = true;
    },
    triggerConfirmDialog(offerId) {
      const offer = this.appraisal.offers.find((o) => o.id === offerId);
      if (offer) {
        this.selectedOffer = offer;
        this.showConfirmDialog = true;
      }
    },
    async confirmSelection() {
      try {
        if (this.selectedOffer) {
          // Call the API to select the offer as the winner
          await axiosInstance.post(
            `${endpoints.makeWinner(this.selectedOffer.id)}`
          );

          // Update the winner in the local state
          this.appraisal.winner = { offer_id: this.selectedOffer.id };

          // Emit an event to notify parent about the change
          this.$emit("offer-selected", this.selectedOffer.id);

          this.showConfirmDialog = false;
        }
      } catch (error) {
        console.error("Error selecting the winner:", error);
      }
    },
    async submitAdjustedOffer(offerId, adjustedAmount) {
      try {
        const appraisalId = this.$route.params.id;
        // Call the API to adjust the offer amount
        await axiosInstance.patch(
          `${endpoints.updateOffer(appraisalId, offerId)}`,
          { adjusted_amount: adjustedAmount }
        );
        // Emit an event to notify parent about the change
        this.$emit("offer-updated", { offerId, adjustedAmount });
        this.showAdjustInputPopup = false;
      } catch (error) {
        console.error("Error adjusting the offer amount:", error);
      }
    },
    cancelSelection() {
      this.showConfirmDialog = false;
    },
    cancelAdjustInput() {
      this.showAdjustInputPopup = false;
    },
  },
};
</script>

<style scoped>
/* Offers List */
.offers-container {
  width: 100%;
  padding: 20px;
  box-sizing: border-box;
}

.offers-table {
  width: 100%;
  border-collapse: collapse;
  margin: 10px auto;
}

.offers-table th,
.offers-table td {
  text-align: left;
  padding: 8px 12px;
  font-size: 14px;
}

.offers-table th {
  background-color: #f8f9fa;
  color: #6c757d;
  font-weight: 600;
}

.offers-table tr:nth-child(even) {
  background-color: #f9f9f9;
}

.offers-table tr:hover {
  background-color: #f1f1f1;
  cursor: pointer;
}

.actions-cell {
  position: relative;
}

.actions-icon {
  cursor: pointer;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  width: 150px;
  background-color: white;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 10px;
  z-index: 9999;
}

.dropdown-menu button {
  background: none;
  border: none;
  color: #000;
  padding: 8px 12px;
  cursor: pointer;
  width: 100%;
  text-align: left;
}

.dropdown-menu button:hover {
  background-color: #f8f9fa;
}

.adjust-offer-container {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.adjusted-offer-input {
  width: 150px;
  padding: 6px 10px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 14px;
}

.submit-offer-button {
  background-color: #f26764;
  color: #ffffff;
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.3s ease;
}

.submit-offer-button:hover {
  background-color: #a34947;
}

.submit-offer-button:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(40, 167, 69, 0.25);
}

.winning-row td {
  background-color: #d4edda; /* Light green background */
}

.confirm-dialog {
  position: fixed;
  top: 50%;
  left: 60%;
  transform: translate(-50%, -50%);
  background-color: #fff;
  border: 1px solid #ccc;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
  z-index: 9999;
  width: 300px;
  text-align: center;
}

.confirm-dialog p {
  margin: 0 0 20px;
  font-size: 16px;
  color: #333;
}

.confirm-dialog button {
  background-color: #f26764;
  border: none;
  border-radius: 4px;
  color: #fff;
  cursor: pointer;
  font-size: 16px;
  margin: 0 10px;
  padding: 10px 20px;
  transition: background-color 0.3s ease;
}

.confirm-dialog button:hover {
  background-color: #8f201e;
}

.confirm-dialog button:last-child {
  background-color: #6c757d;
}

.confirm-dialog button:last-child:hover {
  background-color: #5a6268;
}

/* Adjust Offer Popup Styles */
.adjust-offer-popup {
  position: fixed;
  top: 50%;
  left: 60%;
  transform: translate(-50%, -50%);
  background-color: #fff;
  border: 1px solid #ccc;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
  z-index: 9999;
  width: 320px;
  text-align: center;
}

.adjust-offer-popup h3 {
  font-size: 18px;
  margin-bottom: 15px;
  color: #333;
}

.adjust-offer-popup .offer-id {
  font-size: 14px;
  color: #666;
  margin-bottom: 15px;
}

.adjust-offer-popup label {
  display: block;
  font-size: 16px;
  margin-bottom: 10px;
  color: #333;
}

.adjust-offer-popup input {
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 16px;
  padding: 10px;
  width: calc(100% - 22px); /* Adjust for padding and border */
  margin-bottom: 20px;
}

.adjust-offer-popup .button-container {
  display: flex;
  justify-content: space-between;
}

.adjust-offer-popup .submit-offer-button,
.adjust-offer-popup .cancel-offer-button {
  background-color: #f26764;
  border: none;
  border-radius: 4px;
  color: #fff;
  cursor: pointer;
  font-size: 16px;
  padding: 10px 20px;
  transition: background-color 0.3s ease;
  flex: 1;
  margin: 0 5px;
}

.adjust-offer-popup .submit-offer-button {
  background-color: #f26764;
}

.adjust-offer-popup .submit-offer-button:hover {
  background-color: #8f201e;
}

.adjust-offer-popup .cancel-offer-button {
  background-color: #6c757d;
}

.adjust-offer-popup .cancel-offer-button:hover {
  background-color: #888888;
}

/* No Offers */
.no-offers-message {
  text-align: center;
  font-size: 16px;
  color: #6c757d;
  padding: 20px;
}
</style>
