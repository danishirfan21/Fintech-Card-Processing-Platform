/**
 * Dashboard Component
 * Main dashboard showing cards, transactions, and account summary
 */
import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Button,
  Box,
  CircularProgress,
  AppBar,
  Toolbar,
  IconButton,
} from '@mui/material';
import { Add as AddIcon, Logout as LogoutIcon, Refresh as RefreshIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useSnackbar } from 'notistack';
import apiService from '../services/api';
import { User, VirtualCard, Transaction, AccountSummary } from '../types';
import CardList from './CardList';
import TransactionList from './TransactionList';
import CreateCardDialog from './CreateCardDialog';
import CreateTransactionDialog from './CreateTransactionDialog';
import AccountSummaryCard from './AccountSummaryCard';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();

  const [user, setUser] = useState<User | null>(null);
  const [cards, setCards] = useState<VirtualCard[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [accountSummary, setAccountSummary] = useState<AccountSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [openCardDialog, setOpenCardDialog] = useState(false);
  const [openTransactionDialog, setOpenTransactionDialog] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [userData, cardsData, transactionsData, summaryData] = await Promise.all([
        apiService.getCurrentUser(),
        apiService.getCards(),
        apiService.getTransactions(),
        apiService.getAccountSummary(),
      ]);

      setUser(userData);
      setCards(cardsData.results);
      setTransactions(transactionsData.results);
      setAccountSummary(summaryData);
    } catch (err) {
      const errorMessage = apiService.handleError(err);
      enqueueSnackbar(errorMessage, { variant: 'error' });

      // If unauthorized, redirect to login
      if (errorMessage.includes('401') || errorMessage.includes('authentication')) {
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    apiService.logout();
    enqueueSnackbar('Logged out successfully', { variant: 'success' });
    navigate('/login');
  };

  const handleCardCreated = () => {
    setOpenCardDialog(false);
    loadDashboardData();
    enqueueSnackbar('Card created successfully', { variant: 'success' });
  };

  const handleTransactionCreated = () => {
    setOpenTransactionDialog(false);
    loadDashboardData();
    enqueueSnackbar('Transaction processed successfully', { variant: 'success' });
  };

  const handleCardAction = async () => {
    await loadDashboardData();
  };

  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Fintech Card Platform
          </Typography>
          <Typography variant="body1" sx={{ mr: 2 }}>
            {user?.username}
          </Typography>
          <IconButton color="inherit" onClick={loadDashboardData} sx={{ mr: 1 }}>
            <RefreshIcon />
          </IconButton>
          <IconButton color="inherit" onClick={handleLogout}>
            <LogoutIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Grid container spacing={3}>
          {/* Account Summary */}
          <Grid item xs={12}>
            <AccountSummaryCard summary={accountSummary} />
          </Grid>

          {/* Action Buttons */}
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setOpenCardDialog(true)}
              >
                Create Card
              </Button>
              <Button
                variant="contained"
                color="secondary"
                startIcon={<AddIcon />}
                onClick={() => setOpenTransactionDialog(true)}
                disabled={cards.length === 0}
              >
                New Transaction
              </Button>
            </Box>
          </Grid>

          {/* Cards Section */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h5" gutterBottom>
                My Cards
              </Typography>
              {cards.length === 0 ? (
                <Typography color="text.secondary">
                  No cards yet. Create your first card to get started!
                </Typography>
              ) : (
                <CardList cards={cards} onCardAction={handleCardAction} />
              )}
            </Paper>
          </Grid>

          {/* Transactions Section */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h5" gutterBottom>
                Recent Transactions
              </Typography>
              {transactions.length === 0 ? (
                <Typography color="text.secondary">
                  No transactions yet. Create a transaction to see it here!
                </Typography>
              ) : (
                <TransactionList transactions={transactions} />
              )}
            </Paper>
          </Grid>
        </Grid>
      </Container>

      {/* Dialogs */}
      <CreateCardDialog
        open={openCardDialog}
        onClose={() => setOpenCardDialog(false)}
        onSuccess={handleCardCreated}
      />
      <CreateTransactionDialog
        open={openTransactionDialog}
        onClose={() => setOpenTransactionDialog(false)}
        onSuccess={handleTransactionCreated}
        cards={cards}
      />
    </>
  );
};

export default Dashboard;
