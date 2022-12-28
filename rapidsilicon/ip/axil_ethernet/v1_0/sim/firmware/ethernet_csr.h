#ifndef __ETHERNET_CSR_H
#define __ETHERNET_CSR_H
#include <stdint.h>
#include <system.h>
#ifndef CSR_ACCESSORS_DEFINED
#include <hw/common.h>
#endif /* ! CSR_ACCESSORS_DEFINED */
#define ETHERNET_CSR_BASE 0x30000000L

/* ethphy */
#define CSR_ETHPHY_BASE (ETHERNET_CSR_BASE + 0x800L)
#define CSR_ETHPHY_CRG_RESET_ADDR (ETHERNET_CSR_BASE + 0x800L)
#define CSR_ETHPHY_CRG_RESET_SIZE 1
static inline uint32_t ethphy_crg_reset_read(void) {
	return csr_read_simple((ETHERNET_CSR_BASE + 0x800L));
}
static inline void ethphy_crg_reset_write(uint32_t v) {
	csr_write_simple(v, (ETHERNET_CSR_BASE + 0x800L));
}
#define CSR_ETHPHY_MDIO_W_ADDR (ETHERNET_CSR_BASE + 0x804L)
#define CSR_ETHPHY_MDIO_W_SIZE 1
static inline uint32_t ethphy_mdio_w_read(void) {
	return csr_read_simple((ETHERNET_CSR_BASE + 0x804L));
}
static inline void ethphy_mdio_w_write(uint32_t v) {
	csr_write_simple(v, (ETHERNET_CSR_BASE + 0x804L));
}
#define CSR_ETHPHY_MDIO_W_MDC_OFFSET 0
#define CSR_ETHPHY_MDIO_W_MDC_SIZE 1
static inline uint32_t ethphy_mdio_w_mdc_extract(uint32_t oldword) {
	uint32_t mask = ((uint32_t)(1 << 1)-1);
	return ( (oldword >> 0) & mask );
}
static inline uint32_t ethphy_mdio_w_mdc_read(void) {
	uint32_t word = ethphy_mdio_w_read();
	return ethphy_mdio_w_mdc_extract(word);
}
static inline uint32_t ethphy_mdio_w_mdc_replace(uint32_t oldword, uint32_t plain_value) {
	uint32_t mask = ((uint32_t)(1 << 1)-1);
	return (oldword & (~(mask << 0))) | (mask & plain_value)<< 0 ;
}
static inline void ethphy_mdio_w_mdc_write(uint32_t plain_value) {
	uint32_t oldword = ethphy_mdio_w_read();
	uint32_t newword = ethphy_mdio_w_mdc_replace(oldword, plain_value);
	ethphy_mdio_w_write(newword);
}
#define CSR_ETHPHY_MDIO_W_OE_OFFSET 1
#define CSR_ETHPHY_MDIO_W_OE_SIZE 1
static inline uint32_t ethphy_mdio_w_oe_extract(uint32_t oldword) {
	uint32_t mask = ((uint32_t)(1 << 1)-1);
	return ( (oldword >> 1) & mask );
}
static inline uint32_t ethphy_mdio_w_oe_read(void) {
	uint32_t word = ethphy_mdio_w_read();
	return ethphy_mdio_w_oe_extract(word);
}
static inline uint32_t ethphy_mdio_w_oe_replace(uint32_t oldword, uint32_t plain_value) {
	uint32_t mask = ((uint32_t)(1 << 1)-1);
	return (oldword & (~(mask << 1))) | (mask & plain_value)<< 1 ;
}
static inline void ethphy_mdio_w_oe_write(uint32_t plain_value) {
	uint32_t oldword = ethphy_mdio_w_read();
	uint32_t newword = ethphy_mdio_w_oe_replace(oldword, plain_value);
	ethphy_mdio_w_write(newword);
}
#define CSR_ETHPHY_MDIO_W_W_OFFSET 2
#define CSR_ETHPHY_MDIO_W_W_SIZE 1
static inline uint32_t ethphy_mdio_w_w_extract(uint32_t oldword) {
	uint32_t mask = ((uint32_t)(1 << 1)-1);
	return ( (oldword >> 2) & mask );
}
static inline uint32_t ethphy_mdio_w_w_read(void) {
	uint32_t word = ethphy_mdio_w_read();
	return ethphy_mdio_w_w_extract(word);
}
static inline uint32_t ethphy_mdio_w_w_replace(uint32_t oldword, uint32_t plain_value) {
	uint32_t mask = ((uint32_t)(1 << 1)-1);
	return (oldword & (~(mask << 2))) | (mask & plain_value)<< 2 ;
}
static inline void ethphy_mdio_w_w_write(uint32_t plain_value) {
	uint32_t oldword = ethphy_mdio_w_read();
	uint32_t newword = ethphy_mdio_w_w_replace(oldword, plain_value);
	ethphy_mdio_w_write(newword);
}
#define CSR_ETHPHY_MDIO_R_ADDR (ETHERNET_CSR_BASE + 0x808L)
#define CSR_ETHPHY_MDIO_R_SIZE 1
static inline uint32_t ethphy_mdio_r_read(void) {
	return csr_read_simple((ETHERNET_CSR_BASE + 0x808L));
}
#define CSR_ETHPHY_MDIO_R_R_OFFSET 0
#define CSR_ETHPHY_MDIO_R_R_SIZE 1
static inline uint32_t ethphy_mdio_r_r_extract(uint32_t oldword) {
	uint32_t mask = ((uint32_t)(1 << 1)-1);
	return ( (oldword >> 0) & mask );
}
static inline uint32_t ethphy_mdio_r_r_read(void) {
	uint32_t word = ethphy_mdio_r_read();
	return ethphy_mdio_r_r_extract(word);
}

/* ethmac */
#define CSR_ETHMAC_BASE (ETHERNET_CSR_BASE + 0x1000L)
#define CSR_ETHMAC_SRAM_WRITER_SLOT_ADDR (ETHERNET_CSR_BASE + 0x1000L)
#define CSR_ETHMAC_SRAM_WRITER_SLOT_SIZE 1
static inline uint32_t ethmac_sram_writer_slot_read(void) {
	return csr_read_simple((ETHERNET_CSR_BASE + 0x1000L));
}
#define CSR_ETHMAC_SRAM_WRITER_LENGTH_ADDR (ETHERNET_CSR_BASE + 0x1004L)
#define CSR_ETHMAC_SRAM_WRITER_LENGTH_SIZE 1
static inline uint32_t ethmac_sram_writer_length_read(void) {
	return csr_read_simple((ETHERNET_CSR_BASE + 0x1004L));
}
#define CSR_ETHMAC_SRAM_WRITER_ERRORS_ADDR (ETHERNET_CSR_BASE + 0x1008L)
#define CSR_ETHMAC_SRAM_WRITER_ERRORS_SIZE 1
static inline uint32_t ethmac_sram_writer_errors_read(void) {
	return csr_read_simple((ETHERNET_CSR_BASE + 0x1008L));
}
#define CSR_ETHMAC_SRAM_WRITER_EV_STATUS_ADDR (ETHERNET_CSR_BASE + 0x100cL)
#define CSR_ETHMAC_SRAM_WRITER_EV_STATUS_SIZE 1
static inline uint32_t ethmac_sram_writer_ev_status_read(void) {
	return csr_read_simple((ETHERNET_CSR_BASE + 0x100cL));
}
#define CSR_ETHMAC_SRAM_WRITER_EV_STATUS_AVAILABLE_OFFSET 0
#define CSR_ETHMAC_SRAM_WRITER_EV_STATUS_AVAILABLE_SIZE 1
static inline uint32_t ethmac_sram_writer_ev_status_available_extract(uint32_t oldword) {
	uint32_t mask = ((uint32_t)(1 << 1)-1);
	return ( (oldword >> 0) & mask );
}
static inline uint32_t ethmac_sram_writer_ev_status_available_read(void) {
	uint32_t word = ethmac_sram_writer_ev_status_read();
	return ethmac_sram_writer_ev_status_available_extract(word);
}
#define CSR_ETHMAC_SRAM_WRITER_EV_PENDING_ADDR (ETHERNET_CSR_BASE + 0x1010L)
#define CSR_ETHMAC_SRAM_WRITER_EV_PENDING_SIZE 1
static inline uint32_t ethmac_sram_writer_ev_pending_read(void) {
	return csr_read_simple((ETHERNET_CSR_BASE + 0x1010L));
}
static inline void ethmac_sram_writer_ev_pending_write(uint32_t v) {
	csr_write_simple(v, (ETHERNET_CSR_BASE + 0x1010L));
}
#define CSR_ETHMAC_SRAM_WRITER_EV_PENDING_AVAILABLE_OFFSET 0
#define CSR_ETHMAC_SRAM_WRITER_EV_PENDING_AVAILABLE_SIZE 1
static inline uint32_t ethmac_sram_writer_ev_pending_available_extract(uint32_t oldword) {
	uint32_t mask = ((uint32_t)(1 << 1)-1);
	return ( (oldword >> 0) & mask );
}
static inline uint32_t ethmac_sram_writer_ev_pending_available_read(void) {
	uint32_t word = ethmac_sram_writer_ev_pending_read();
	return ethmac_sram_writer_ev_pending_available_extract(word);
}
static inline uint32_t ethmac_sram_writer_ev_pending_available_replace(uint32_t oldword, uint32_t plain_value) {
	uint32_t mask = ((uint32_t)(1 << 1)-1);
	return (oldword & (~(mask << 0))) | (mask & plain_value)<< 0 ;
}
static inline void ethmac_sram_writer_ev_pending_available_write(uint32_t plain_value) {
	uint32_t oldword = ethmac_sram_writer_ev_pending_read();
	uint32_t newword = ethmac_sram_writer_ev_pending_available_replace(oldword, plain_value);
	ethmac_sram_writer_ev_pending_write(newword);
}
#define CSR_ETHMAC_SRAM_WRITER_EV_ENABLE_ADDR (ETHERNET_CSR_BASE + 0x1014L)
#define CSR_ETHMAC_SRAM_WRITER_EV_ENABLE_SIZE 1
static inline uint32_t ethmac_sram_writer_ev_enable_read(void) {
	return csr_read_simple((ETHERNET_CSR_BASE + 0x1014L));
}
static inline void ethmac_sram_writer_ev_enable_write(uint32_t v) {
	csr_write_simple(v, (ETHERNET_CSR_BASE + 0x1014L));
}
#define CSR_ETHMAC_SRAM_WRITER_EV_ENABLE_AVAILABLE_OFFSET 0
#define CSR_ETHMAC_SRAM_WRITER_EV_ENABLE_AVAILABLE_SIZE 1
static inline uint32_t ethmac_sram_writer_ev_enable_available_extract(uint32_t oldword) {
	uint32_t mask = ((uint32_t)(1 << 1)-1);
	return ( (oldword >> 0) & mask );
}
static inline uint32_t ethmac_sram_writer_ev_enable_available_read(void) {
	uint32_t word = ethmac_sram_writer_ev_enable_read();
	return ethmac_sram_writer_ev_enable_available_extract(word);
}
static inline uint32_t ethmac_sram_writer_ev_enable_available_replace(uint32_t oldword, uint32_t plain_value) {
	uint32_t mask = ((uint32_t)(1 << 1)-1);
	return (oldword & (~(mask << 0))) | (mask & plain_value)<< 0 ;
}
static inline void ethmac_sram_writer_ev_enable_available_write(uint32_t plain_value) {
	uint32_t oldword = ethmac_sram_writer_ev_enable_read();
	uint32_t newword = ethmac_sram_writer_ev_enable_available_replace(oldword, plain_value);
	ethmac_sram_writer_ev_enable_write(newword);
}
#define CSR_ETHMAC_SRAM_READER_START_ADDR (ETHERNET_CSR_BASE + 0x1018L)
#define CSR_ETHMAC_SRAM_READER_START_SIZE 1
static inline uint32_t ethmac_sram_reader_start_read(void) {
	return csr_read_simple((ETHERNET_CSR_BASE + 0x1018L));
}
static inline void ethmac_sram_reader_start_write(uint32_t v) {
	csr_write_simple(v, (ETHERNET_CSR_BASE + 0x1018L));
}
#define CSR_ETHMAC_SRAM_READER_READY_ADDR (ETHERNET_CSR_BASE + 0x101cL)
#define CSR_ETHMAC_SRAM_READER_READY_SIZE 1
static inline uint32_t ethmac_sram_reader_ready_read(void) {
	return csr_read_simple((ETHERNET_CSR_BASE + 0x101cL));
}
#define CSR_ETHMAC_SRAM_READER_LEVEL_ADDR (ETHERNET_CSR_BASE + 0x1020L)
#define CSR_ETHMAC_SRAM_READER_LEVEL_SIZE 1
static inline uint32_t ethmac_sram_reader_level_read(void) {
	return csr_read_simple((ETHERNET_CSR_BASE + 0x1020L));
}
#define CSR_ETHMAC_SRAM_READER_SLOT_ADDR (ETHERNET_CSR_BASE + 0x1024L)
#define CSR_ETHMAC_SRAM_READER_SLOT_SIZE 1
static inline uint32_t ethmac_sram_reader_slot_read(void) {
	return csr_read_simple((ETHERNET_CSR_BASE + 0x1024L));
}
static inline void ethmac_sram_reader_slot_write(uint32_t v) {
	csr_write_simple(v, (ETHERNET_CSR_BASE + 0x1024L));
}
#define CSR_ETHMAC_SRAM_READER_LENGTH_ADDR (ETHERNET_CSR_BASE + 0x1028L)
#define CSR_ETHMAC_SRAM_READER_LENGTH_SIZE 1
static inline uint32_t ethmac_sram_reader_length_read(void) {
	return csr_read_simple((ETHERNET_CSR_BASE + 0x1028L));
}
static inline void ethmac_sram_reader_length_write(uint32_t v) {
	csr_write_simple(v, (ETHERNET_CSR_BASE + 0x1028L));
}
#define CSR_ETHMAC_SRAM_READER_EV_STATUS_ADDR (ETHERNET_CSR_BASE + 0x102cL)
#define CSR_ETHMAC_SRAM_READER_EV_STATUS_SIZE 1
static inline uint32_t ethmac_sram_reader_ev_status_read(void) {
	return csr_read_simple((ETHERNET_CSR_BASE + 0x102cL));
}
#define CSR_ETHMAC_SRAM_READER_EV_STATUS_EVENT0_OFFSET 0
#define CSR_ETHMAC_SRAM_READER_EV_STATUS_EVENT0_SIZE 1
static inline uint32_t ethmac_sram_reader_ev_status_event0_extract(uint32_t oldword) {
	uint32_t mask = ((uint32_t)(1 << 1)-1);
	return ( (oldword >> 0) & mask );
}
static inline uint32_t ethmac_sram_reader_ev_status_event0_read(void) {
	uint32_t word = ethmac_sram_reader_ev_status_read();
	return ethmac_sram_reader_ev_status_event0_extract(word);
}
#define CSR_ETHMAC_SRAM_READER_EV_PENDING_ADDR (ETHERNET_CSR_BASE + 0x1030L)
#define CSR_ETHMAC_SRAM_READER_EV_PENDING_SIZE 1
static inline uint32_t ethmac_sram_reader_ev_pending_read(void) {
	return csr_read_simple((ETHERNET_CSR_BASE + 0x1030L));
}
static inline void ethmac_sram_reader_ev_pending_write(uint32_t v) {
	csr_write_simple(v, (ETHERNET_CSR_BASE + 0x1030L));
}
#define CSR_ETHMAC_SRAM_READER_EV_PENDING_EVENT0_OFFSET 0
#define CSR_ETHMAC_SRAM_READER_EV_PENDING_EVENT0_SIZE 1
static inline uint32_t ethmac_sram_reader_ev_pending_event0_extract(uint32_t oldword) {
	uint32_t mask = ((uint32_t)(1 << 1)-1);
	return ( (oldword >> 0) & mask );
}
static inline uint32_t ethmac_sram_reader_ev_pending_event0_read(void) {
	uint32_t word = ethmac_sram_reader_ev_pending_read();
	return ethmac_sram_reader_ev_pending_event0_extract(word);
}
static inline uint32_t ethmac_sram_reader_ev_pending_event0_replace(uint32_t oldword, uint32_t plain_value) {
	uint32_t mask = ((uint32_t)(1 << 1)-1);
	return (oldword & (~(mask << 0))) | (mask & plain_value)<< 0 ;
}
static inline void ethmac_sram_reader_ev_pending_event0_write(uint32_t plain_value) {
	uint32_t oldword = ethmac_sram_reader_ev_pending_read();
	uint32_t newword = ethmac_sram_reader_ev_pending_event0_replace(oldword, plain_value);
	ethmac_sram_reader_ev_pending_write(newword);
}
#define CSR_ETHMAC_SRAM_READER_EV_ENABLE_ADDR (ETHERNET_CSR_BASE + 0x1034L)
#define CSR_ETHMAC_SRAM_READER_EV_ENABLE_SIZE 1
static inline uint32_t ethmac_sram_reader_ev_enable_read(void) {
	return csr_read_simple((ETHERNET_CSR_BASE + 0x1034L));
}
static inline void ethmac_sram_reader_ev_enable_write(uint32_t v) {
	csr_write_simple(v, (ETHERNET_CSR_BASE + 0x1034L));
}
#define CSR_ETHMAC_SRAM_READER_EV_ENABLE_EVENT0_OFFSET 0
#define CSR_ETHMAC_SRAM_READER_EV_ENABLE_EVENT0_SIZE 1
static inline uint32_t ethmac_sram_reader_ev_enable_event0_extract(uint32_t oldword) {
	uint32_t mask = ((uint32_t)(1 << 1)-1);
	return ( (oldword >> 0) & mask );
}
static inline uint32_t ethmac_sram_reader_ev_enable_event0_read(void) {
	uint32_t word = ethmac_sram_reader_ev_enable_read();
	return ethmac_sram_reader_ev_enable_event0_extract(word);
}
static inline uint32_t ethmac_sram_reader_ev_enable_event0_replace(uint32_t oldword, uint32_t plain_value) {
	uint32_t mask = ((uint32_t)(1 << 1)-1);
	return (oldword & (~(mask << 0))) | (mask & plain_value)<< 0 ;
}
static inline void ethmac_sram_reader_ev_enable_event0_write(uint32_t plain_value) {
	uint32_t oldword = ethmac_sram_reader_ev_enable_read();
	uint32_t newword = ethmac_sram_reader_ev_enable_event0_replace(oldword, plain_value);
	ethmac_sram_reader_ev_enable_write(newword);
}
#define CSR_ETHMAC_PREAMBLE_CRC_ADDR (ETHERNET_CSR_BASE + 0x1038L)
#define CSR_ETHMAC_PREAMBLE_CRC_SIZE 1
static inline uint32_t ethmac_preamble_crc_read(void) {
	return csr_read_simple((ETHERNET_CSR_BASE + 0x1038L));
}
#define CSR_ETHMAC_RX_DATAPATH_PREAMBLE_ERRORS_ADDR (ETHERNET_CSR_BASE + 0x103cL)
#define CSR_ETHMAC_RX_DATAPATH_PREAMBLE_ERRORS_SIZE 1
static inline uint32_t ethmac_rx_datapath_preamble_errors_read(void) {
	return csr_read_simple((ETHERNET_CSR_BASE + 0x103cL));
}
#define CSR_ETHMAC_RX_DATAPATH_CRC_ERRORS_ADDR (ETHERNET_CSR_BASE + 0x1040L)
#define CSR_ETHMAC_RX_DATAPATH_CRC_ERRORS_SIZE 1
static inline uint32_t ethmac_rx_datapath_crc_errors_read(void) {
	return csr_read_simple((ETHERNET_CSR_BASE + 0x1040L));
}

#endif
