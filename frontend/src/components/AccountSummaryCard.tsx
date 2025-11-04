/**
 * AccountSummaryCard Component
 * Displays account summary with key metrics
 */
import React from 'react';
import { Paper, Grid, Typography, Box } from '@mui/material';
import {
  AccountBalance,
  CreditCard,
  TrendingUp,
  TrendingDown,
} from '@mui/icons-material';
import { AccountSummary } from '../types';

interface AccountSummaryCardProps {
  summary: AccountSummary | null;
}

const AccountSummaryCard: React.FC<AccountSummaryCardProps> = ({ summary }) => {
  if (!summary) {
    return null;
  }

  const summaryItems = [
    {
      title: 'Total Balance',
      value: `$${parseFloat(summary.total_balance).toFixed(2)}`,
      icon: <AccountBalance fontSize="large" />,
      color: '#1976d2',
    },
    {
      title: 'Active Cards',
      value: `${summary.active_cards} / ${summary.total_cards}`,
      icon: <CreditCard fontSize="large" />,
      color: '#2e7d32',
    },
    {
      title: 'Total Credited',
      value: `$${parseFloat(summary.total_credited).toFixed(2)}`,
      icon: <TrendingUp fontSize="large" />,
      color: '#388e3c',
    },
    {
      title: 'Total Debited',
      value: `$${parseFloat(summary.total_debited).toFixed(2)}`,
      icon: <TrendingDown fontSize="large" />,
      color: '#d32f2f',
    },
  ];

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Account Summary
      </Typography>
      <Grid container spacing={3} sx={{ mt: 1 }}>
        {summaryItems.map((item, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                p: 2,
                borderRadius: 2,
                backgroundColor: `${item.color}15`,
              }}
            >
              <Box sx={{ color: item.color, mr: 2 }}>{item.icon}</Box>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  {item.title}
                </Typography>
                <Typography variant="h6">{item.value}</Typography>
              </Box>
            </Box>
          </Grid>
        ))}
      </Grid>
      <Box sx={{ mt: 2 }}>
        <Typography variant="body2" color="text.secondary">
          Total Transactions: {summary.total_transactions}
        </Typography>
        {summary.last_transaction_date && (
          <Typography variant="body2" color="text.secondary">
            Last Transaction:{' '}
            {new Date(summary.last_transaction_date).toLocaleString()}
          </Typography>
        )}
      </Box>
    </Paper>
  );
};

export default AccountSummaryCard;
