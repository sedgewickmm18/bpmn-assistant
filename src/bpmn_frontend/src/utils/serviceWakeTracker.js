import { isHostedVersion } from '../config';

const SERVICE_KEYS = Object.freeze({
  ASSISTANT: 'assistant',
  LAYOUT: 'layout',
});

const serviceWakeState = {
  [SERVICE_KEYS.ASSISTANT]: false,
  [SERVICE_KEYS.LAYOUT]: false,
};

/**
 * Returns true the first time a hosted service is accessed so the UI
 * can surface a wake-up notice. Subsequent calls for the same service
 * return false.
 *
 * @param {string} serviceKey - Identifier from SERVICE_KEYS.
 * @returns {boolean} whether a wake notice should be shown.
 */
export function consumeWakeNotice(serviceKey) {
  if (!isHostedVersion) {
    return false;
  }

  if (!Object.prototype.hasOwnProperty.call(serviceWakeState, serviceKey)) {
    return false;
  }

  if (serviceWakeState[serviceKey]) {
    return false;
  }

  serviceWakeState[serviceKey] = true;
  return true;
}

export function resetWakeNotice(serviceKey) {
  if (!isHostedVersion) {
    return;
  }

  if (!Object.prototype.hasOwnProperty.call(serviceWakeState, serviceKey)) {
    return;
  }

  serviceWakeState[serviceKey] = false;
}

export { SERVICE_KEYS as wakeServiceKeys };
