import { getAPIUrl } from './util';
import { DashboardRequest } from '@/types/types';

export const submitAPRepairRequest = async () => {
  var response = await fetch(`${getAPIUrl()}ap-repair-request`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  })
  return response;
}

export const submitAPRequest = async (formData: DashboardRequest) => {
  var response = await fetch(`${getAPIUrl()}ap-request`, {
    method: 'POST',
    body: JSON.stringify(formData),
    headers: {
      'Content-Type': 'application/json'
    }
  })
  return response;
}

export const submitAPDeleteRequest = async () => {
  var response = await fetch(`${getAPIUrl()}ap-request`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json'
    }
  })
  return response;
}

export const submitSlurmRequest = async () => {
  var response = await fetch(`${getAPIUrl()}slurm-request`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  })
  return response;
}
