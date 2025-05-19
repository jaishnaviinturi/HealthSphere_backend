import mongoose from 'mongoose';

const healthRecordSchema = new mongoose.Schema({
  id: {
    type: String,
    required: true,
    default: () => new mongoose.Types.ObjectId().toString(), // Unique ID for each record
  },
  medicalCondition: {
    type: String,
    required: true,
  },
  monthsSince: {
    type: Number,
    required: true,
  },
  currentMedications: {
    type: String,
    required: true,
  },
  date: {
    type: String,
    required: true,
  },
  fileName: {
    type: String,
    required: false,
  },
  filePath: {
    type: String,
    required: false,
  },
});

const patientSchema = new mongoose.Schema({
  fullName: {
    type: String,
    required: true,
  },
  email: {
    type: String,
    required: true,
    unique: true,
  },
  password: {
    type: String,
    required: true,
  },
  contactNumber: {
    type: String,
    required: true,
  },
  healthRecords: [healthRecordSchema], // Array of health records
});

export default mongoose.model('Patient', patientSchema);