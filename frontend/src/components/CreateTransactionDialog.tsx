/**
 * CreateTransactionDialog Component
 * Dialog for processing a new transaction
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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { useSnackbar } from 'notistack';
import apiService from '../services/api';
import { VirtualCard } from '../types';

interface CreateTransactionDialogProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  cards: VirtualCard[];
}

const CreateTransactionDialog: React.FC<CreateTransactionDialogProps> = ({
  open,
  onClose,
  onSuccess,
  cards,
}) => {
  const { enqueueSnackbar } = useSnackbar();

  const [formData, setFormData] = useState({
    card_id: '',
    transaction_type: 'CREDIT',
    amount: '',
    description: '',
  });
  const [loading, setLoading] = useState(false);

  const activeCards = cards.filter((card) => card.status === 'ACTIVE');

  const handleChange = (e: any) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await apiService.processTransaction({
        card_id: parseInt(formData.card_id),
        transaction_type: formData.transaction_type as 'CREDIT' | 'DEBIT',
        amount: formData.amount,
        description: formData.description,
      });
      onSuccess();
      setFormData({
        card_id: '',
        transaction_type: 'CREDIT',
        amount: '',
        description: '',
      });
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
        <DialogTitle>Process Transaction</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Card</InputLabel>
            <Select
              name="card_id"
              value={formData.card_id}
              onChange={handleChange}
              label="Card"
              required
              disabled={loading}
            >
              {activeCards.map((card) => (
                <MenuItem key={card.id} value={card.id}>
                  {card.card_holder_name} - {card.masked_card_number} (Balance: $
                  {parseFloat(card.balance).toFixed(2)})
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Transaction Type</InputLabel>
            <Select
              name="transaction_type"
              value={formData.transaction_type}
              onChange={handleChange}
              label="Transaction Type"
              required
              disabled={loading}
            >
              <MenuItem value="CREDIT">Credit (Add Funds)</MenuItem>
              <MenuItem value="DEBIT">Debit (Spend Funds)</MenuItem>
            </Select>
          </FormControl>

          <TextField
            margin="dense"
            name="amount"
            label="Amount"
            type="number"
            fullWidth
            required
            value={formData.amount}
            onChange={handleChange}
            disabled={loading}
            inputProps={{ min: 0.01, step: 0.01 }}
            sx={{ mt: 2 }}
          />

          <TextField
            margin="dense"
            name="description"
            label="Description"
            type="text"
            fullWidth
            required
            value={formData.description}
            onChange={handleChange}
            disabled={loading}
            multiline
            rows={2}
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button type="submit" variant="contained" disabled={loading}>
            {loading ? <CircularProgress size={24} /> : 'Process Transaction'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default CreateTransactionDialog;
