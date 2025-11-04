/**
 * TransactionList Component
 * Displays a table of transactions
 */
import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Typography,
} from '@mui/material';
import { ArrowUpward, ArrowDownward } from '@mui/icons-material';
import { Transaction } from '../types';

interface TransactionListProps {
  transactions: Transaction[];
}

const TransactionList: React.FC<TransactionListProps> = ({ transactions }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return 'success';
      case 'PENDING':
        return 'warning';
      case 'FAILED':
        return 'error';
      case 'REVERSED':
        return 'default';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <TableContainer sx={{ mt: 2 }}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Type</TableCell>
            <TableCell>Card</TableCell>
            <TableCell>Description</TableCell>
            <TableCell align="right">Amount</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Date</TableCell>
            <TableCell>Reference</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {transactions.map((transaction) => (
            <TableRow key={transaction.id} hover>
              <TableCell>
                {transaction.transaction_type === 'CREDIT' ? (
                  <Chip
                    icon={<ArrowDownward />}
                    label="Credit"
                    color="success"
                    size="small"
                  />
                ) : (
                  <Chip
                    icon={<ArrowUpward />}
                    label="Debit"
                    color="error"
                    size="small"
                  />
                )}
              </TableCell>
              <TableCell>
                <Typography variant="body2">
                  {transaction.card_masked_number}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {transaction.card_holder_name}
                </Typography>
              </TableCell>
              <TableCell>{transaction.description}</TableCell>
              <TableCell align="right">
                <Typography
                  variant="body2"
                  color={
                    transaction.transaction_type === 'CREDIT' ? 'success.main' : 'error.main'
                  }
                >
                  {transaction.transaction_type === 'CREDIT' ? '+' : '-'}$
                  {parseFloat(transaction.amount).toFixed(2)}
                </Typography>
              </TableCell>
              <TableCell>
                <Chip
                  label={transaction.status}
                  color={getStatusColor(transaction.status)}
                  size="small"
                />
              </TableCell>
              <TableCell>
                <Typography variant="body2">
                  {formatDate(transaction.created_at)}
                </Typography>
              </TableCell>
              <TableCell>
                <Typography variant="caption" color="text.secondary">
                  {transaction.reference_number}
                </Typography>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default TransactionList;
