/**
 * CardList Component
 * Displays a list of virtual cards
 */
import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  Button,
  Box,
} from '@mui/material';
import {
  CreditCard as CardIcon,
  Block as BlockIcon,
  CheckCircle as CheckIcon,
} from '@mui/icons-material';
import { VirtualCard } from '../types';
import apiService from '../services/api';
import { useSnackbar } from 'notistack';

interface CardListProps {
  cards: VirtualCard[];
  onCardAction: () => void;
}

const CardList: React.FC<CardListProps> = ({ cards, onCardAction }) => {
  const { enqueueSnackbar } = useSnackbar();

  const handleBlockCard = async (cardId: number) => {
    try {
      await apiService.blockCard(cardId);
      enqueueSnackbar('Card blocked successfully', { variant: 'success' });
      onCardAction();
    } catch (err) {
      const errorMessage = apiService.handleError(err);
      enqueueSnackbar(errorMessage, { variant: 'error' });
    }
  };

  const handleUnblockCard = async (cardId: number) => {
    try {
      await apiService.unblockCard(cardId);
      enqueueSnackbar('Card unblocked successfully', { variant: 'success' });
      onCardAction();
    } catch (err) {
      const errorMessage = apiService.handleError(err);
      enqueueSnackbar(errorMessage, { variant: 'error' });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return 'success';
      case 'BLOCKED':
        return 'error';
      case 'EXPIRED':
        return 'default';
      default:
        return 'default';
    }
  };

  return (
    <Grid container spacing={2} sx={{ mt: 1 }}>
      {cards.map((card) => (
        <Grid item xs={12} sm={6} md={4} key={card.id}>
          <Card
            sx={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              minHeight: 200,
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <CardIcon />
                <Chip
                  label={card.status}
                  color={getStatusColor(card.status)}
                  size="small"
                />
              </Box>

              <Typography variant="h6" gutterBottom>
                {card.masked_card_number}
              </Typography>

              <Typography variant="body2" sx={{ mb: 1 }}>
                {card.card_holder_name}
              </Typography>

              <Typography variant="caption" sx={{ mb: 2, display: 'block' }}>
                Expires: {new Date(card.expiry_date).toLocaleDateString()}
              </Typography>

              <Typography variant="h5" sx={{ mb: 2 }}>
                ${parseFloat(card.balance).toFixed(2)}
              </Typography>

              {card.status === 'ACTIVE' ? (
                <Button
                  size="small"
                  variant="outlined"
                  startIcon={<BlockIcon />}
                  onClick={() => handleBlockCard(card.id)}
                  sx={{ color: 'white', borderColor: 'white' }}
                >
                  Block Card
                </Button>
              ) : card.status === 'BLOCKED' ? (
                <Button
                  size="small"
                  variant="outlined"
                  startIcon={<CheckIcon />}
                  onClick={() => handleUnblockCard(card.id)}
                  sx={{ color: 'white', borderColor: 'white' }}
                >
                  Unblock Card
                </Button>
              ) : null}
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

export default CardList;
