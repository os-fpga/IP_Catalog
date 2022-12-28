#include "ethernet.h"

#include <stdio.h>
#include <generated/csr.h>
#include <generated/mem.h>
#include "ethernet_csr.h"

/*-----------------------------------------------------------------------*/
/* Constants                                                             */
/*-----------------------------------------------------------------------*/

#define ETHMAC_EV_SRAM_WRITER 0x1
#define ETHMAC_EV_SRAM_READER 0x1

#define ETHMAC_BASE 0x00020000L
#define ETHMAC_RX_SLOTS 2
#define ETHMAC_TX_SLOTS 2
#define ETHMAC_SLOT_SIZE 2048

#define ETHMAC_RX_SLOT0_BASE AXIL_ETHERNET_BASE + ETHMAC_BASE + 0 * ETHMAC_SLOT_SIZE
#define ETHMAC_RX_SLOT1_BASE AXIL_ETHERNET_BASE + ETHMAC_BASE + 1 * ETHMAC_SLOT_SIZE
#define ETHMAC_TX_SLOT0_BASE AXIL_ETHERNET_BASE + ETHMAC_BASE + 2 * ETHMAC_SLOT_SIZE
#define ETHMAC_TX_SLOT1_BASE AXIL_ETHERNET_BASE + ETHMAC_BASE + 2 * ETHMAC_SLOT_SIZE

/*-----------------------------------------------------------------------*/
/* Init                                                                  */
/*-----------------------------------------------------------------------*/

static void eth_init(void) {
  /* Make sure to clear pending events */
  ethmac_sram_reader_ev_pending_write(ETHMAC_EV_SRAM_READER);
  ethmac_sram_writer_ev_pending_write(ETHMAC_EV_SRAM_WRITER);
}

/*-----------------------------------------------------------------------*/
/* Send Packet                                                           */
/*-----------------------------------------------------------------------*/

static void eth_send_packet(uint8_t txslot, uint16_t txlen)
{
  /* Wait buffer to be available */
  while(!(ethmac_sram_reader_ready_read()));

  /* Fill slot, length and send */
  ethmac_sram_reader_slot_write(txslot);
  ethmac_sram_reader_length_write(txlen);
  ethmac_sram_reader_start_write(1);
}

/*-----------------------------------------------------------------------*/
/* Receive Packet                                                        */
/*-----------------------------------------------------------------------*/

static void eth_receive_packet(uint8_t *rxslot, uint16_t *rxlen)
{
  while ((ethmac_sram_writer_ev_pending_read() & ETHMAC_EV_SRAM_WRITER) == 0)
    printf(".");
  printf("\n");
  *rxslot = ethmac_sram_writer_slot_read();
  *rxlen  = ethmac_sram_writer_length_read();
}

/*-----------------------------------------------------------------------*/
/* Simple TX/RX loopback test                                            */
/*-----------------------------------------------------------------------*/

void test_loopback(void) {
  volatile uint8_t *txslot0 = (uint8_t *) ETHMAC_TX_SLOT0_BASE;
  volatile uint8_t *rxslot0 = (uint8_t *) ETHMAC_RX_SLOT0_BASE;
  volatile uint8_t *rxslot1 = (uint8_t *) ETHMAC_RX_SLOT1_BASE;

  uint16_t i;
  uint8_t  txslot;
  uint16_t  txlen;
  uint8_t  rxslot;
  uint16_t  rxlen;

  /* Initialize Ethernet */
  eth_init();

  /* Send packet on TX Slot0 */
  txslot = 0;
  txlen  = 64;
  txslot0[0] = 0x01;
  txslot0[1] = 0x02;
  txslot0[2] = 0x03;
  txslot0[3] = 0x04;
  eth_send_packet(txslot, txlen);

  /* Receive packet on RX Slot0 or 1 */
  eth_receive_packet(&rxslot, &rxlen);
  ethmac_sram_writer_ev_pending_write(ETHMAC_EV_SRAM_WRITER);
  printf("RX Slot: %d, Len: %d, Data: ", rxslot, rxlen);
  for (i=0; i<rxlen; i++) {
    if (rxslot == 0)
      printf("0x%02x ", rxslot0[i]);
    else
      printf("0x%02x ", rxslot1[i]);
  }
  printf("\n");
}
