'use client';

import { DashboardRequest, RequestStatus, UserInfo } from '@/types/types';
import { ArrowPathIcon } from '@heroicons/react/24/solid';
import { useEffect, useState } from 'react';
import { submitAPRequest, submitAPDeleteRequest } from './api';

interface APFormProps {
  data: UserInfo;
  onSubmit: (formData: DashboardRequest) => void;
  onCancel: () => void;
}

const textInputClass = "w-full px-4 py-2 border border-gray-300 rounded-md disabled:bg-gray-100 disabled:text-gray-500"
const checkboxClass = "w-5 h-5 text-blue-600 rounded border-gray-300 cursor-pointer disabled:cursor-default"


export default function APForm({data, onSubmit, onCancel}: APFormProps) {
  const [formData, setFormData] = useState<DashboardRequest>({
    job_input_size: 1,
    job_output_size: 1,
    job_count: 10000,
    concurrent_jobs: 10000,
    dagman: false,
    local_universe: false,
  });

  const [sendingForm, setSendingForm] = useState({
    sending: false,
    error: "",
  });

  useEffect(() => {
    if(data && data.dashboard_request_status !== RequestStatus.NOT_REQUESTED && data.dashboard_request_info){
      setFormData(data.dashboard_request_info);
    }
  }, [data]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    if (!/^\d*$/.test(value)) {
      return; // Only allow numeric input
    }
    setFormData(prev => ({
      ...prev,
      [name]: Number(value),
    }));
  };

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: checked,
    }));
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    console.log('Form submitted:', formData);

    setSendingForm({sending: true, error: ""});
    var response = await submitAPRequest(formData);
    if (!response.ok) {
      setSendingForm({sending: false, error: `Error submitting form: ${response.statusText}`});
    } else {
      setSendingForm({sending: false, error: ""});
      onSubmit(formData);
    }
  };

  const handleCancel = async (e: React.MouseEvent) => {
    e.preventDefault();
    console.log('Form cancelled.');

    setSendingForm({sending: true, error: ""});
    var response = await submitAPDeleteRequest();
    if (!response.ok) {
      setSendingForm({sending: false, error: `Error cancelling request: ${response.statusText}`});
    } else {
      setSendingForm({sending: false, error: ""});
      onCancel();  
    }
  };

  const disabled = data.dashboard_request_status !== RequestStatus.NOT_REQUESTED;

  return (
    <form onSubmit={handleSubmit}>
      <div className="grid grid-cols-2 gap-6 mb-8">
        {/* Job Input Size */}
        <div>
          <label htmlFor="job_input_size" className="block text-md font-medium text-gray-700 mb-2">
            Job Input Size (GB)
          </label>
          <input
            type="text"
            id="job_input_size"
            name="job_input_size"
            pattern="[0-9]*"
            disabled={disabled}
            value={formData.job_input_size}
            onChange={handleInputChange}
            className={textInputClass}
            placeholder="1"
          />
        </div>

        {/* Job Output Size */}
        <div>
          <label htmlFor="job_output_size" className="block text-md font-medium text-gray-700 mb-2">
            Job Output Size (GB)
          </label>
          <input
            type="text"
            id="job_output_size"
            name="job_output_size"
            pattern="[0-9]*"
            value={formData.job_output_size}
            disabled={disabled}
            onChange={handleInputChange}
            className={textInputClass}
            placeholder="1"
          />
        </div>

        {/* Total Job Count */}
        <div>
          <label htmlFor="job_count" className="block text-md font-medium text-gray-700 mb-2">
            Total Job Count
          </label>
          <input
            type="text"
            id="job_count"
            name="job_count"
            pattern="[0-9]*"
            disabled={disabled}
            value={formData.job_count}
            onChange={handleInputChange}
            className={textInputClass}
            placeholder="10000"
          />
        </div>

        {/* Concurrent Job Count */}
        <div>
          <label htmlFor="concurrent_jobs" className="block text-md font-medium text-gray-700 mb-2">
            Concurrent Job Count
          </label>
          <input
            type="text"
            id="concurrent_jobs"
            name="concurrent_jobs"
            pattern="[0-9]*"
            disabled={disabled}
            value={formData.concurrent_jobs}
            onChange={handleInputChange}
            className={textInputClass}
            placeholder="10000"
          />
        </div>
      </div>

      <div className="space-y-4 mb-8">
        {/* Dagman Checkbox */}
        <label className="flex items-center cursor-pointer">
          <input
            type="checkbox"
            name="dagman"
            disabled={disabled}
            checked={formData.dagman}
            onChange={handleCheckboxChange}
            className={checkboxClass}
          />
          <span className="ml-3 text-md text-gray-700">
            Do you plan on running multi-stage workflows with DagMAN?
          </span>
        </label>

        {/* Local Universe Checkbox */}
        <label className="flex items-center cursor-pointer">
          <input
            type="checkbox"
            name="local_universe"
            disabled={disabled}
            checked={formData.local_universe}
            onChange={handleCheckboxChange}
            className={checkboxClass}
          />
          <span className="ml-3 text-md text-gray-700">
            Do you plan on running local universe jobs directly on your AP?
          </span>
        </label>
      </div>

      {/* Submit Buttons */}
      {!disabled && !sendingForm.sending && 
        <div className="flex justify-between">
          <button
            className="px-0 py-2 bg-none text-blue-600 font-medium rounded-md hover:text-blue-700 cursor-pointer"
          >
            Request Defaults
          </button>

          <button
            type="submit"
            className="px-6 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 cursor-pointer"
          >
            Submit
          </button>
        </div>
      }
      {/* Request in progress spinner for submit button */}
      {!disabled && sendingForm.sending &&
        <div className="flex justify-end">
          <button
            type="button"
            className="px-6 py-2 bg-none text-blue-600 rounded-md"
          >
            <ArrowPathIcon className='size-6 animate-spin'/>
          </button>
        </div>
      }
      {/* Cancel button */}
      {disabled && !sendingForm.sending &&
        <div className="flex justify-end">
          <button
            type="button"
            onClick={(e)=>handleCancel(e)}
            className="px-6 py-2 bg-none text-red-600 font-medium rounded-md hover:text-red-700 cursor-pointer"
          >
            Cancel Request
          </button>
        </div>
      }
      {/* Request in progress spinner for cancel button */}
      {disabled && sendingForm.sending &&
        <div className="flex justify-end">
          <button
            type="button"
            className="px-6 py-2 bg-none text-red-600 rounded-md"
          >
            <ArrowPathIcon className='size-6 animate-spin'/>
          </button>
        </div>
      }
    </form>
  );
}
