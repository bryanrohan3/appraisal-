<template>
  <div>
    <h1>Appraisal Details</h1>
    <div v-if="appraisal">
      <p>ID: {{ appraisal.id }}</p>
      <p>
        Client Name: {{ appraisal.customer_first_name }}
        {{ appraisal.customer_last_name }}
      </p>
      <p>Car Make: {{ appraisal.vehicle_make }}</p>
      <p>Car Model: {{ appraisal.vehicle_model }}</p>
      <p>VIN: {{ appraisal.vehicle_vin }}</p>
      <p>Rego: {{ appraisal.vehicle_registration }}</p>
      <p>Status: {{ appraisal.status }}</p>
      <p>
        Initiating Dealer: {{ appraisal.initiating_dealer.first_name }}
        {{ appraisal.initiating_dealer.last_name }}
      </p>
    </div>
    <div v-else>
      <p>There is no appraisal with this ID.</p>
    </div>
  </div>
</template>

<script>
import { axiosInstance, endpoints } from "@/helpers/axiosHelper";

export default {
  name: "AppraisalViewPage",
  data() {
    return {
      appraisal: null,
    };
  },
  created() {
    this.fetchAppraisal();
  },
  methods: {
    fetchAppraisal() {
      const id = this.$route.params.id;
      axiosInstance
        .get(`${endpoints.all_appraisals}${id}/`)
        .then((response) => {
          this.appraisal = response.data;
        })
        .catch((error) => {
          console.error("Error fetching appraisal details:", error);
        });
    },
  },
};
</script>
