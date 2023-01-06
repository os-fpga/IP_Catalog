#include <generated/csr.h>
#include <generated/soc.h>
#include <irq.h>
#include <uart.h>
#include <stdio.h>

void isr(void);

void isr(void)
{
	__attribute__((unused)) unsigned int irqs;

	irqs = irq_pending() & irq_getmask();

#ifndef UART_POLLING
	if(irqs & (1 << UART_INTERRUPT))
		uart_isr();
#endif
}
