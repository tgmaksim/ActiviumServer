<template>
    <RouterView />

    <AppDialog
        :visible="showInstallDialog"
        :title="strings.titleDialogPwaInstall"
        :message="dialogMessage"
        :action-text="dialogActionText"
        :cancel-text="strings.buttonDialogPwaInstallCancel"
        @action="handleInstallAction"
        @cancel="dismissInstallDialog"
    />
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { RouterView } from "vue-router";

import AppDialog from "@/components/AppDialog.vue";
import { strings } from "@/constants/strings";

import {
    getPwaPlatform,
    shouldShowInstallPrompt,
    promptPwaInstall,
    hideInstallPrompt,
} from "@/utils/pwa-install";

const showInstallDialog = ref(false);
const showManualInstructions = ref(false);

const platform = getPwaPlatform();

const dialogMessage = computed(() => {
    if (!showManualInstructions.value) {
        return strings.messageDialogPwaInstallIntro;
    }

    switch (platform) {
        case "android":
            return strings.messageDialogPwaInstallAndroid;

        case "ios":
            return strings.messageDialogPwaInstallIos;

        default:
            return strings.messageDialogPwaInstallOther;
    }
});

const dialogActionText = computed(() =>
    showManualInstructions.value
        ? strings.buttonDialogPwaInstallManual
        : strings.buttonDialogPwaInstall,
);

onMounted(() => {
    showInstallDialog.value =
        shouldShowInstallPrompt();
});

async function handleInstallAction(): Promise<void> {
    if (showManualInstructions.value) {
        showInstallDialog.value = false;
        return;
    }

    const outcome = await promptPwaInstall();

    if (outcome === "accepted") {
        showInstallDialog.value = false;
        return;
    }

    if (outcome === "unavailable") {
        showManualInstructions.value = true;
    }
}

function dismissInstallDialog(): void {
    hideInstallPrompt();
    showInstallDialog.value = false;
}
</script>