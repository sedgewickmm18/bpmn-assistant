<template>
  <v-select
    label="Model"
    density="compact"
    :items="availableModels"
    :modelValue="selectedModel"
    @update:modelValue="onModelChange"
    :list-props="{ density: 'compact' }"
    no-data-text="Please provide API keys to access models"
  ></v-select>
</template>

<script>
const Models = Object.freeze({
  GPT_4O_MINI: "gpt-4o-mini",
  GPT_4O: "gpt-4o",
  HAIKU_3_5: "claude-3-5-haiku-20241022",
  SONNET_3_5: "claude-3-5-sonnet-20241022",
  GEMINI_1_5_PRO: "gemini-1.5-pro",
  GEMINI_2_FLASH: "gemini-2.0-flash-exp",
});

const Providers = Object.freeze({
  OPENAI: "openai",
  ANTHROPIC: "anthropic",
  GOOGLE: "google",
});

export default {
  name: "ModelPicker",
  data() {
    return {
      selectedModel: "",
      models: [
        {
          value: Models.GPT_4O_MINI,
          title: "GPT-4o mini",
          provider: Providers.OPENAI,
        },
        { value: Models.GPT_4O, title: "GPT-4o", provider: Providers.OPENAI },
        {
          value: Models.HAIKU_3_5,
          title: "Claude 3.5 Haiku",
          provider: Providers.ANTHROPIC,
        },
        {
          value: Models.SONNET_3_5,
          title: "Claude 3.5 Sonnet",
          provider: Providers.ANTHROPIC,
        },
        {
          value: Models.GEMINI_2_FLASH,
          title: "Gemini 2.0 Flash",
          provider: Providers.GOOGLE,
        },
        {
          value: Models.GEMINI_1_5_PRO,
          title: "Gemini 1.5 Pro",
          provider: Providers.GOOGLE,
        },
      ],
      availableProviders: [],
    };
  },
  computed: {
    availableModels() {
      return this.models.filter((model) =>
        this.availableProviders.includes(model.provider)
      );
    },
  },
  methods: {
    onModelChange(model) {
      this.selectedModel = model;
      this.$emit("select-model", model);
    },
    async fetchAvailableProviders() {
      try {
        const response = await fetch(
          "http://localhost:8000/available_providers",
          {
            method: "GET",
            headers: { "Content-Type": "application/json" },
          }
        );

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        this.availableProviders = Object.keys(data).filter(
          (provider) => data[provider]
        );

        if (this.availableProviders.includes(Providers.OPENAI)) {
          this.onModelChange(Models.GPT_4O);
        } else if (this.availableProviders.includes(Providers.ANTHROPIC)) {
          this.onModelChange(Models.SONNET_3_5);
        } else if (this.availableProviders.includes(Providers.GOOGLE)) {
          this.onModelChange(Models.GEMINI_1_5_PRO);
        }
      } catch (error) {
        console.error("Error fetching available providers", error);
      }
    },
  },
  mounted() {
    this.fetchAvailableProviders();
  },
};
</script>
