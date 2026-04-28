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

const jobDataSizeOptions = [
  "Not sure",
  "< 10",
  "10 - 100",
  "100 - 500",
  "> 500",
];


export default function APForm({data, onSubmit, onCancel}: APFormProps) {
  const [formData, setFormData] = useState<DashboardRequest>({
    job_data_size: "Not sure",
    job_count: 1000,
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

  const handleRadioChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
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
      <div className="grid grid-cols-1 gap-6 mb-8">
        
        {/* Total Job Count */}
        <div>
          <label htmlFor="job_count" className="block text-md font-medium text-gray-700 mb-2">
            How many jobs do you plan on running?
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
            placeholder="1000"
          />
        </div>
        
        {/* Job Input Size */}
        <div>
          <span className="block text-md font-medium text-gray-700 mb-2">
            How much disk space does each of your jobs need (in GB)? Include the size of both input and output data.
          </span>
          <div className="flex flex-row gap-2">
            {jobDataSizeOptions.map((option) => (
              <label
                key={option}
                className={`flex flex-1 items-center justify-start gap-2 px-2 py-2 rounded-md cursor-pointer transition-colors ${
                  disabled ? "cursor-default bg-gray-100 text-gray-500" :
                  formData.job_data_size === option ? "text-blue-700" : ""
                }`}
              >
                <input
                  type="radio"
                  name="job_data_size"
                  value={option}
                  disabled={disabled}
                  checked={formData.job_data_size === option}
                  onChange={handleRadioChange}
                  className="w-4 h-4 text-blue-600 border-gray-300 cursor-pointer disabled:cursor-default"
                />
                <span className="text-md font-medium">{option}</span>
              </label>
            ))}
          </div>
        </div>

      </div>

      <div className="space-y-4 mb-8">
        <label className="block text-md font-medium text-gray-700 mb-2">
          Advanced Configuration
        </label>
        
        <p className="text-md text-gray-600 mb-2">
          If you are already familiar with HTCondor, these configuration options will influence your AP's
          resource requirements. These can be left blank by default.
        </p>
        
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
            Do you plan on running multi-stage workflows via DAGMan?
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
            Do you plan on running jobs directly on your AP via Local Universe?
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
