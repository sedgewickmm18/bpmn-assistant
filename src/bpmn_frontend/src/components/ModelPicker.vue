<template>
  <v-select
    class="model-picker"
    placeholder="Select model"
    density="compact"
    :items="availableModels"
    :modelValue="selectedModel"
    @update:modelValue="onModelChange"
    hide-details
    :list-props="{ density: 'compact' }"
    no-data-text="Please provide API keys"
    variant="outlined"
  ></v-select>
</template>

<script>
import { ref, onMounted } from 'vue'
import { Ollama } from 'ollama'

const ollama = new Ollama({host: 'http://127.0.0.1:11434'})
const Models2 = ref([])
const loadItems = async () => {
  try {
    const response = await ollama.list()
    Models2.value = response.data
  } catch (err) {
    console.error("Failed to load items:", err)
  }
}
console.log(Models2)

const Models = Object.freeze({
  OLLAMA_GRANITE4: 'ollama_chat/granite4',
});

const Providers = Object.freeze({
  OPENAI: 'openai',
  ANTHROPIC: 'anthropic',
  GOOGLE: 'google',
  FIREWORKS_AI: 'fireworks_ai',
  OLLAMA: 'ollama'
});

export default {
  name: 'ModelPicker',
  data() {
    return {
      selectedModel: '',
/*
      models: [
        {
          value: Models.OLLAMA_GRANITE4,
          title: 'ollama_chat/granite4',
          provider: Providers.OLLAMA
        },
      ],
*/
      availableModels: [],
      availableProviders: [],
    };
  },
/*
  compute: {
    availableModels() {
      return this.models.filter((model) =>
        this.availableProviders.includes(model.provider)
      );
    },
  },
*/
  methods: {
    onModelChange(model) {
      this.selectedModel = model;
      this.$emit('select-model', model);
    },
    async fetchAvailableProviders() {
      try {
        const response = await fetch(
          'http://localhost:8000/available_providers',
          {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
          }
        );

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        this.availableProviders = Object.keys(data).filter(
          (provider) => data[provider]
        );
	console.log(Object.values(data))
	this.availableModels = Object.values(data).filter((val) => val).flat()

	/*
        if (this.availableProviders.includes(Providers.OPENAI)) {
          this.onModelChange(Models.GPT_5);
        } else if (this.availableProviders.includes(Providers.ANTHROPIC)) {
          this.onModelChange(Models.SONNET_4);
        } else if (this.availableProviders.includes(Providers.GOOGLE)) {
          this.onModelChange(Models.GEMINI_2_5_PRO);
        } else if (this.availableProviders.includes(Providers.FIREWORKS_AI)) {
          this.onModelChange(Models.LLAMA_4_MAVERICK);
        } else if (this.availableProviders.includes(Providers.OLLAMA)) {
          this.onModelChange(Models.OLLAMA_GRANITE4);
        }
	*/
      } catch (error) {
        console.error('Error fetching available providers', error);
      }
    },
  },
  mounted() {
    this.fetchAvailableProviders();
  },
};
</script>

<style scoped>
.model-picker {
  width: 400px;
}
</style>
