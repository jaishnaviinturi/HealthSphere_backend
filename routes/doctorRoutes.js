import express from 'express';
import { addDoctor, loginDoctor, getDoctorsByHospital, deleteDoctor } from '../controllers/doctorController.js'; // Add new controllers
import { authMiddleware } from '../middleware/authMiddleware.js';
import { getDoctorAppointments,getDoctorPatientRecords } from '../controllers/appointmentController.js'; // Import the new controller

const router = express.Router();

// Protected route: Only authenticated hospitals can add doctors
router.post('/:hospitalId/doctors', authMiddleware('hospital'), addDoctor);

// Public route: Doctor login
router.post('/login', loginDoctor);

// Protected route: Get doctor's approved appointments
router.get('/:doctorId/appointments', authMiddleware('doctor'), getDoctorAppointments);

// Protected route: Get all doctors for a hospital
router.get('/:hospitalId/doctors', authMiddleware('hospital'), getDoctorsByHospital);

// Protected route: Delete a doctor
router.delete('/:hospitalId/doctors/:doctorId', authMiddleware('hospital'), deleteDoctor);

router.get('/:doctorId/patient-records', authMiddleware('doctor'), getDoctorPatientRecords);

export default router;