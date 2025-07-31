import React from 'react';
import { EmailStatus } from './EmailList';

interface Props {
  data: EmailStatus;
}

const EmailCard: React.FC<Props> = ({ data }) => {
  const { account, inbox, spam, not_found } = data;

  let status = 'Not Found';
  let color = 'gray';

  if (inbox) {
    status = 'Inbox';
    color = 'green';
  } else if (spam) {
    status = 'Spam';
    color = 'yellow';
  }

  return (
    <div className={`border-l-4 border-${color}-500 bg-white shadow p-4 rounded`}>
      <h2 className="font-semibold">{account}</h2>
      <p className="text-sm text-gray-600">Status: {status}</p>
    </div>
  );
};

export default EmailCard;
