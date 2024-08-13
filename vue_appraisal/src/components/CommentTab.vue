<template>
  <div class="comment-tab-container">
    <!-- Tabs for switching between General and Private Comments -->
    <div class="tabs">
      <button
        :class="{ active: currentTab === 'general' }"
        @click="currentTab = 'general'"
      >
        General Comments
      </button>
      <button
        :class="{ active: currentTab === 'private' }"
        @click="currentTab = 'private'"
      >
        Private Comments
      </button>
    </div>

    <!-- General Comments Section -->
    <div v-if="currentTab === 'general'" class="comment-section">
      <h3>General Comments</h3>
      <div v-if="(appraisal.general_comments?.length || 0) > 0">
        <div
          v-for="comment in appraisal.general_comments"
          :key="comment.id"
          class="comment"
        >
          <div class="comment-header">
            <span class="comment-user">{{
              comment.user ? comment.user.username : "Unknown User"
            }}</span>
            <span class="comment-date">{{
              formatDate(comment.comment_date_time)
            }}</span>
          </div>
          <p class="comment-body">{{ comment.comment }}</p>
        </div>
      </div>
      <div v-else class="no-comments">No general comments available.</div>
    </div>

    <!-- Private Comments Section -->
    <div v-if="currentTab === 'private'" class="comment-section">
      <h3>Private Comments</h3>
      <div v-if="(appraisal.private_comments?.length || 0) > 0">
        <div
          v-for="comment in appraisal.private_comments"
          :key="comment.id"
          class="comment private-comment"
        >
          <div class="comment-header">
            <span class="comment-user">{{
              comment.user ? comment.user.username : "Unknown User"
            }}</span>
            <span class="comment-date">{{
              formatDate(comment.comment_date_time)
            }}</span>
          </div>
          <p class="comment-body">{{ comment.comment }}</p>
        </div>
      </div>
      <div v-else class="no-comments">No private comments available.</div>
    </div>

    <!-- Comment Input Form -->
    <div class="comment-form">
      <textarea
        v-model="newComment"
        placeholder="Write your comment here..."
      ></textarea>
      <div class="form-controls">
        <button @click="addComment">Add Comment</button>
      </div>
    </div>
  </div>
</template>

<script>
import { axiosInstance, endpoints } from "@/helpers/axiosHelper";

export default {
  name: "CommentTab",
  props: {
    appraisal: {
      type: Object,
      required: true,
      default: () => ({
        general_comments: [],
        private_comments: [],
      }),
    },
  },
  data() {
    return {
      currentTab: "general", // The current tab ('general' or 'private')
      newComment: "",
      currentUser: {
        username: "Me", // Placeholder, update as needed
      },
    };
  },
  methods: {
    formatDate(dateString) {
      const options = {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      };
      return new Date(dateString).toLocaleDateString(undefined, options);
    },
    async addComment() {
      if (!this.newComment.trim()) {
        alert("Comment cannot be empty.");
        return;
      }

      // Ensure currentUser is defined
      if (!this.currentUser || !this.currentUser.username) {
        alert("User information is not available.");
        return;
      }

      // Create a new comment object
      const newComment = {
        comment: this.newComment,
        comment_date_time: new Date().toISOString(),
      };

      // Determine the correct endpoint based on the current tab
      const endpoint =
        this.currentTab === "general"
          ? endpoints.addGeneralComment(this.appraisal.id)
          : endpoints.addPrivateComment(this.appraisal.id);

      try {
        // Send the new comment to the backend
        const response = await axiosInstance.post(endpoint, newComment);

        if (response.status === 201) {
          // Add the new comment to the local `appraisal` object
          const updatedComment = {
            ...newComment,
            id: response.data.id,
            user: this.currentUser, // Assuming the backend sends user info
          };
          if (this.currentTab === "general") {
            this.appraisal.general_comments.push(updatedComment);
          } else {
            this.appraisal.private_comments.push(updatedComment);
          }

          // Clear the input
          this.newComment = "";
        } else {
          console.error("Error adding comment:", response.statusText);
        }
      } catch (error) {
        console.error(
          "Error adding comment:",
          error.response ? error.response.data : error.message
        );
      }
    },

    async refreshComments() {
      try {
        const { data } = await axiosInstance.get(
          endpoints.getAppraisal(this.appraisal.id)
        );
        this.$emit("update:appraisal", data);
      } catch (error) {
        console.error("Error refreshing comments:", error);
      }
    },
  },
};
</script>

<style scoped>
.comment-tab-container {
  padding: 20px;
}

.tabs {
  display: flex;
  margin-bottom: 20px;
  position: relative;
  padding-left: 0;
  padding-right: 0;
  justify-content: flex-start; /* Align tabs to the left */
}

.tabs button {
  background-color: transparent;
  border: none;
  padding: 10px 20px; /* Adjust padding as needed */
  margin-right: 10px; /* Add space between buttons */
  cursor: pointer;
  font-size: 12px;
  text-align: center;
  color: #b0b0b0;
  position: relative;
  cursor: pointer;
}

.tabs button.active {
  color: #333;
  font-weight: 600;
  border-bottom: 2px solid #eb5a58;
}

.comment-section {
  margin-bottom: 20px;
}

.comment-section h3 {
  margin-bottom: 10px;
  font-size: 1.2em;
}

.comment {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  margin-bottom: 10px;
  background-color: #f9f9f9;
}

.private-comment {
  border-left: 5px solid #eb5a58;
  background-color: #fff3e0;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.comment-user {
  font-weight: bold;
}

.comment-date {
  color: #888;
}

.comment-body {
  margin: 0;
}

.no-comments {
  color: #777;
  font-style: italic;
}

.comment-form {
  margin-top: 20px;
}

.comment-form textarea {
  width: 100%;
  height: 80px;
  padding: 10px;
  margin-bottom: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  box-sizing: border-box;
}

.form-controls {
  display: flex;
  justify-content: flex-end;
}

.form-controls button {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  background-color: #eb5a58;
  color: #fff;
  cursor: pointer;
}

.form-controls button:hover {
  background-color: #0056b3;
}
</style>
