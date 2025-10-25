import React from 'react';

interface ScrollStackItemProps {
  children: React.ReactNode;
}

export const ScrollStackItem: React.FC<ScrollStackItemProps> = ({ children }) => {
  return <div className="scroll-stack-item">{children}</div>;
};

interface ScrollStackProps {
  children: React.ReactNode;
}

const ScrollStack: React.FC<ScrollStackProps> = ({ children }) => {
  return (
    <div className="scroll-stack">
      {children}
    </div>
  );
};

export default ScrollStack;
