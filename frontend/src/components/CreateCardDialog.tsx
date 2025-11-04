/**
 * CreateCardDialog Component
 * Dialog for creating a new virtual card
 */
import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  CircularProgress,
} from '@mui/material';
import { useSnackbar } from 'notistack';
import apiService from '../services/api';

interface CreateCardDialogProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const CreateCardDialog: React.FC<CreateCardDialogProps> = ({ open, onClose, onSuccess }) => {
  const { enqueueSnackbar } = useSnackbar();

  const [formData, setFormData] = useState({
    card_holder_name: '',
    initial_balance: '0.00',
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await apiService.createCard(formData);
      onSuccess();
      setFormData({ card_holder_name: '', initial_balance: '0.00' });
    } catch (err) {
      const errorMessage = apiService.handleError(err);
      enqueueSnackbar(errorMessage, { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>Create New Card</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            name="card_holder_name"
            label="Card Holder Name"
            type="text"
            fullWidth
            required
            value={formData.card_holder_name}
            onChange={handleChange}
            disabled={loading}
            sx={{ mt: 2 }}
          />
          <TextField
            margin="dense"
            name="initial_balance"
            label="Initial Balance"
            type="number"
            fullWidth
            value={formData.initial_balance}
            onChange={handleChange}
            disabled={loading}
            inputProps={{ min: 0, step: 0.01 }}
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button type="submit" variant="contained" disabled={loading}>
            {loading ? <CircularProgress size={24} /> : 'Create Card'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default CreateCardDialog;
