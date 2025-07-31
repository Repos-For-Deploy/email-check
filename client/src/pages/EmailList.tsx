import React, { useEffect, useState } from 'react';
import EmailCard from './EmailCard';

export interface EmailStatus {
  account: string;
  inbox: boolean;
  spam: boolean;
  not_found: boolean;
}

const EmailList: React.FC = () => {
  const [emails, setEmails] = useState<EmailStatus[]>([]);

  useEffect(() => {
    // Fetch example (adjust API as needed)
    fetch('/api/results')
      .then(res => res.json())
      .then(data => setEmails(data.results || []));
  }, []);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
      {emails.map((email, i) => (
        <EmailCard key={i} data={email} />
      ))}
    </div>
  );
};

export default EmailList;
