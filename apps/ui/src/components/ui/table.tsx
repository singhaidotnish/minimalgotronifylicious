'use client';
import * as React from 'react';

function cx(...parts: Array<string | undefined>) {
  return parts.filter(Boolean).join(' ');
}

type El<P, T> = React.ForwardRefExoticComponent<P & React.RefAttributes<T>>;

const Root = React.forwardRef<HTMLTableElement, React.HTMLAttributes<HTMLTableElement>>(
  ({ className, ...props }, ref) => (
    <table ref={ref} className={cx('w-full text-sm caption-bottom', className)} {...props} />
  )
);
Root.displayName = 'Table';

const Head = React.forwardRef<HTMLTableSectionElement, React.HTMLAttributes<HTMLTableSectionElement>>(
  ({ className, ...props }, ref) => <thead ref={ref} className={cx('[&_tr]:border-b', className)} {...props} />
);
Head.displayName = 'Table.Head';

const Body = React.forwardRef<HTMLTableSectionElement, React.HTMLAttributes<HTMLTableSectionElement>>(
  ({ className, ...props }, ref) => (
    <tbody ref={ref} className={cx('[&_tr:last-child]:border-0', className)} {...props} />
  )
);
Body.displayName = 'Table.Body';

const Row = React.forwardRef<HTMLTableRowElement, React.HTMLAttributes<HTMLTableRowElement>>(
  ({ className, ...props }, ref) => (
    <tr ref={ref} className={cx('border-b transition-colors', className)} {...props} />
  )
);
Row.displayName = 'Table.Row';

const HeadCell = React.forwardRef<HTMLTableCellElement, React.ThHTMLAttributes<HTMLTableCellElement>>(
  ({ className, ...props }, ref) => (
    <th ref={ref} className={cx('h-10 px-2 text-left align-middle font-medium', className)} {...props} />
  )
);
HeadCell.displayName = 'Table.HeadCell';

const Cell = React.forwardRef<HTMLTableCellElement, React.TdHTMLAttributes<HTMLTableCellElement>>(
  ({ className, ...props }, ref) => <td ref={ref} className={cx('p-2 align-middle', className)} {...props} />
);
Cell.displayName = 'Table.Cell';

const Caption = React.forwardRef<HTMLTableCaptionElement, React.HTMLAttributes<HTMLTableCaptionElement>>(
  ({ className, ...props }, ref) => (
    <caption ref={ref} className={cx('mt-2 text-sm text-gray-500', className)} {...props} />
  )
);
Caption.displayName = 'Table.Caption';

type TableCompound = El<React.HTMLAttributes<HTMLTableElement>, HTMLTableElement> & {
  Head: typeof Head;
  HeadCell: typeof HeadCell;
  Body: typeof Body;
  Row: typeof Row;
  Cell: typeof Cell;
  Caption: typeof Caption;
};

export const Table = Object.assign(Root, { Head, HeadCell, Body, Row, Cell, Caption }) as TableCompound;
export default Table;
export { Head as TableHead, HeadCell, Body as TableBody, Row as TableRow, Cell as TableCell, Caption as TableCaption };
